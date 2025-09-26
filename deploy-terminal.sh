#!/bin/bash

# Try available terminal emulators
for term in gnome-terminal konsole xfce4-terminal x-terminal-emulator; do
  if command -v $term &>/dev/null; then
    $term -- bash -c "./deploy.sh; echo; echo '✅ Finished. Press Enter to close.'; read"
    exit 0
  fi
done

echo "❌ No supported terminal emulator found. Run ./deploy.sh manually."
exit 1
