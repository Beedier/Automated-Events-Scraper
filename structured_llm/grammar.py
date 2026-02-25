"""
structured_llm.grammar
~~~~~~~~~~~~~~~~~~~~~~

Converts a Pydantic v2 model into a GBNF (Guided BNF) grammar string.

GBNF is the grammar format used by llama.cpp.  The server will then use
this grammar during *token-level sampling* to make it physically impossible
for the model to produce a token that would violate the grammar — so the
output is structurally correct by construction, not by hope.

How the conversion works
------------------------
1. We call ``model.model_json_schema()`` to get a standard JSON Schema dict.
2. We walk that dict recursively and emit GBNF rules for every type we find.
3. The root rule is always ``root``, which represents the top-level object.

Supported field types
---------------------
- str  → quoted JSON string
- int  → integer (no decimal point)
- float → number (with optional decimal)
- bool → true | false
- None / Optional[X] → null | <X-rule>
- Literal["a","b"] / Enum → enumerated string choices
- list[X] → JSON array of X
- dict[str, X] → JSON object with string keys and X values
- Nested Pydantic models → inline object rule with required fields
"""

from __future__ import annotations

import logging
import re
from typing import Any

from .exceptions import GrammarGenerationError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Low-level GBNF primitives
# These are the building blocks that map directly to JSON grammar fragments.
# ---------------------------------------------------------------------------

_GBNF_PREAMBLE = """\
# Primitives
ws        ::= ([ \\t\\n])*
true      ::= "true"
false     ::= "false"
null      ::= "null"
number    ::= "-"? ([0-9] | [1-9] [0-9]*) ("." [0-9]+)? ([eE] [-+]? [0-9]+)?
integer   ::= "-"? ([0-9] | [1-9] [0-9]*)
string    ::= "\\"" (
                [^\\x00-\\x1f\\\\\\"]
              | "\\\\" (["\\\\bfnrt/] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F])
              )* "\\""
"""


def _rule_name_for_model(model_name: str) -> str:
    """Sanitise a Pydantic model class name into a valid GBNF rule identifier."""
    # GBNF identifiers: letters, digits, hyphens (no underscores in the spec,
    # but llama.cpp is lenient — we use hyphens to be safe).
    sanitised = re.sub(r"[^a-zA-Z0-9]", "-", model_name).strip("-").lower()
    return sanitised or "object"


def _escape_string_for_gbnf(value: str) -> str:
    """Escape a Python string so it is safe inside a GBNF string literal."""
    # We need to double-escape backslashes because the GBNF file itself is a
    # text file — so a literal quote in the enum value needs \\" in GBNF.
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return escaped


# ---------------------------------------------------------------------------
# Main generator class
# ---------------------------------------------------------------------------


class GBNFGrammarGenerator:
    """Converts a Pydantic v2 model class into a GBNF grammar string.

    Usage::

        gen = GBNFGrammarGenerator()
        grammar = gen.generate(MyPydanticModel)
        # grammar is a multiline string ready to send to llama.cpp

    The generator is stateful during a single ``generate`` call (it accumulates
    helper rules).  You can reuse the same instance across multiple calls.
    """

    def generate(self, model: type) -> str:
        """Generate a GBNF grammar string for *model*.

        Parameters
        ----------
        model:
            A Pydantic v2 ``BaseModel`` subclass.

        Returns
        -------
        str
            Complete GBNF grammar.  The ``root`` rule matches the JSON object
            that the model represents.

        Raises
        ------
        GrammarGenerationError
            If the schema contains types we cannot represent in GBNF.
        """
        # Reset per-call state
        self._extra_rules: dict[str, str] = {}  # name -> rule body
        self._schema: dict[str, Any] = {}

        try:
            schema = model.model_json_schema()
        except Exception as exc:
            raise GrammarGenerationError(
                f"Could not extract JSON schema from {model.__name__}: {exc}"
            ) from exc

        logger.debug("JSON Schema for %s: %s", model.__name__, schema)

        self._schema = schema
        # Resolve $defs so we can inline nested models
        self._defs: dict[str, Any] = schema.get("$defs", {})

        root_rule = self._schema_to_rule(schema, rule_name="root")

        lines: list[str] = [_GBNF_PREAMBLE.rstrip()]

        # Emit any helper rules first (they may be referenced by root)
        for name, body in self._extra_rules.items():
            lines.append(f"{name} ::= {body}")

        lines.append(f"root ::= {root_rule}")

        grammar = "\n".join(lines) + "\n"
        logger.debug("Generated GBNF grammar:\n%s", grammar)
        return grammar

    # ------------------------------------------------------------------
    # Internal: schema node → GBNF expression
    # ------------------------------------------------------------------

    def _schema_to_rule(self, schema: dict[str, Any], rule_name: str = "root") -> str:
        """Recursively convert a JSON Schema node to a GBNF rule *expression*.

        Returns an expression string (not a full ``name ::= ...`` line).
        Complex sub-rules are stored in ``self._extra_rules`` and referenced
        by name to avoid duplicating large inline expressions.
        """
        # Handle $ref — pointer to a definition in $defs
        if "$ref" in schema:
            return self._resolve_ref(schema["$ref"], rule_name)

        # Handle anyOf (used by Optional[X] → [X, null])
        if "anyOf" in schema:
            return self._handle_any_of(schema["anyOf"], rule_name)

        schema_type = schema.get("type")

        # ---- Scalar types ----
        if schema_type == "string":
            # enum / Literal → fixed set of quoted values
            if "enum" in schema:
                return self._enum_rule(schema["enum"])
            return "string"

        if schema_type == "integer":
            return "integer"

        if schema_type == "number":
            return "number"

        if schema_type == "boolean":
            return "(true | false)"

        if schema_type == "null":
            return "null"

        # ---- Array ----
        if schema_type == "array":
            return self._array_rule(schema, rule_name)

        # ---- Object ----
        if schema_type == "object" or "properties" in schema:
            return self._object_rule(schema, rule_name)

        # ---- Fallback: if we have an enum at top level without a type ----
        if "enum" in schema:
            return self._enum_rule(schema["enum"])

        raise GrammarGenerationError(
            f"Unsupported schema node (rule '{rule_name}'): {schema!r}\n"
            "If you need support for this type, please open an issue."
        )

    def _resolve_ref(self, ref: str, rule_name: str) -> str:
        """Resolve a JSON Schema ``$ref`` like ``'#/$defs/MyModel'``."""
        # ref format: #/$defs/ModelName
        parts = ref.lstrip("#/").split("/")
        if len(parts) != 2 or parts[0] != "$defs":
            raise GrammarGenerationError(f"Cannot resolve $ref: {ref!r}")

        def_name = parts[1]
        def_schema = self._defs.get(def_name)
        if def_schema is None:
            raise GrammarGenerationError(
                f"$ref '{ref}' not found in schema $defs. "
                f"Available: {list(self._defs.keys())}"
            )

        # Use the definition name as the rule name to avoid collisions
        safe_name = _rule_name_for_model(def_name)

        # Avoid generating the same rule twice
        if safe_name not in self._extra_rules:
            # Temporarily reserve the name to break potential circular refs
            self._extra_rules[safe_name] = "null"  # placeholder
            expr = self._schema_to_rule(def_schema, rule_name=safe_name)
            self._extra_rules[safe_name] = expr

        return safe_name

    def _handle_any_of(self, variants: list[dict[str, Any]], rule_name: str) -> str:
        """Handle ``anyOf`` — typically Optional[X] = [X, {type: null}]."""
        exprs: list[str] = []
        for i, variant in enumerate(variants):
            sub_name = f"{rule_name}-opt{i}"
            expr = self._schema_to_rule(variant, rule_name=sub_name)
            exprs.append(expr)
        return "(" + " | ".join(exprs) + ")"

    def _enum_rule(self, values: list[Any]) -> str:
        """Return a GBNF expression for a fixed set of string/number values."""
        choices: list[str] = []
        for v in values:
            if isinstance(v, str):
                choices.append(f'"\\"" "{_escape_string_for_gbnf(v)}" "\\""')
            elif isinstance(v, bool):
                choices.append("true" if v else "false")
            elif isinstance(v, int | float):
                choices.append(f'"{v}"')
            elif v is None:
                choices.append("null")
            else:
                raise GrammarGenerationError(f"Enum value {v!r} has unsupported type.")
        return "(" + " | ".join(choices) + ")"

    def _array_rule(self, schema: dict[str, Any], rule_name: str) -> str:
        """Return a GBNF expression for a JSON array."""
        items_schema = schema.get("items")
        if items_schema is None:
            # Untyped array — allow any JSON value (we accept any string)
            item_expr = "string"
        else:
            item_expr = self._schema_to_rule(items_schema, rule_name=f"{rule_name}-item")

        # array ::= "[" ws (item (ws "," ws item)*)? ws "]"
        return (
            f'"[" ws ({item_expr} (ws "," ws {item_expr})*)? ws "]"'
        )

    def _object_rule(self, schema: dict[str, Any], rule_name: str) -> str:
        """Return a GBNF expression for a JSON object with known properties."""
        properties: dict[str, Any] = schema.get("properties", {})
        required: list[str] = schema.get("required", [])

        if not properties:
            # Empty or dynamic object — not useful but valid
            return '"{" ws "}"'

        # We emit required fields first (in schema order), then optional ones.
        # All fields are emitted as key-value pairs separated by commas.
        # Optional fields are wrapped in (... )?

        req_fields = [k for k in properties if k in required]
        opt_fields = [k for k in properties if k not in required]

        pairs: list[str] = []

        for field_name in req_fields:
            field_schema = properties[field_name]
            sub_rule_name = f"{rule_name}-{_rule_name_for_model(field_name)}"
            value_expr = self._schema_to_rule(field_schema, rule_name=sub_rule_name)
            # JSON key is always a quoted string
            escaped_key = _escape_string_for_gbnf(field_name)
            pairs.append(f'"\\"" "{escaped_key}" "\\"" ws ":" ws {value_expr}')

        for field_name in opt_fields:
            field_schema = properties[field_name]
            sub_rule_name = f"{rule_name}-{_rule_name_for_model(field_name)}"
            value_expr = self._schema_to_rule(field_schema, rule_name=sub_rule_name)
            escaped_key = _escape_string_for_gbnf(field_name)
            # Optional: whole "," ws "key": value fragment is optional
            opt_pair = f'(ws "," ws "\\"" "{escaped_key}" "\\"" ws ":" ws {value_expr})?'
            pairs.append(opt_pair)

        # Build the full object rule
        if not pairs:
            return '"{" ws "}"'

        # First required pair: "{ key: value"
        # Subsequent required pairs: ", key: value"
        # Optional pairs: already have their own comma

        if req_fields:
            # Start: "{" first_pair
            body = '"{"  ws ' + pairs[0]
            for p in pairs[1 : len(req_fields)]:
                body += ' ws "," ws ' + p
            # Optional fields come after all required ones
            for p in pairs[len(req_fields) :]:
                body += " " + p
            body += ' ws "}"'
        else:
            # No required fields — very unusual but handle gracefully
            # We emit all optional but that's weird; just allow empty object
            body = '"{"  ws '
            # First optional without leading comma
            first = opt_fields[0]
            sub_rule_name = f"{rule_name}-{_rule_name_for_model(first)}"
            first_schema = properties[first]
            first_expr = self._schema_to_rule(first_schema, rule_name=sub_rule_name)
            escaped_key = _escape_string_for_gbnf(first)
            body += f'("\\"" "{escaped_key}" "\\"" ws ":" ws {first_expr}'
            for p in pairs[1:]:
                body += " " + p
            body += ")?"
            body += ' ws "}"'

        return body
