#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
SCRIPT="$SCRIPT_DIR/deploy.sh"

for term in gnome-terminal konsole xfce4-terminal x-terminal-emulator; do
  if command -v $term &>/dev/null; then
    case $term in
      gnome-terminal)
        $term -- bash -c "$SCRIPT; echo; echo '✅ Finished. Press Enter to close.'; read" &
        ;;
      konsole)
        $term -e bash -c "$SCRIPT; echo; echo '✅ Finished. Press Enter to close.'; read" &
        ;;
      xfce4-terminal)
        $term -e "bash -c '$SCRIPT; echo; echo \"✅ Finished. Press Enter to close.\"; read'" &
        ;;
      x-terminal-emulator)
        $term -e bash -c "$SCRIPT; echo; echo '✅ Finished. Press Enter to close.'; read" &
        ;;
    esac
    exit 0
  fi
done

echo "❌ No supported terminal emulator found. Run ./deploy.sh manually."
exit 1
