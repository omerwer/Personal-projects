#!/bin/bash

FILE=".pswd.txt"

# 1. Check if file already exists
if [ -f "$FILE" ]; then
    echo "PIN code already established"
    exit 0
fi

# 2. Prompt user for 6-digit PIN
read -sp "Enter a 6-digit PIN: " PIN
echo

# 3. Validate format
if [[ ! "$PIN" =~ ^[0-9]{6}$ ]]; then
    echo "❌ Invalid input. Please enter exactly 6 digits."
    exit 1
fi

# 4. Hash the PIN using bcrypt via Python
HASHED_PIN=$(python3 -c "import bcrypt; print(bcrypt.hashpw(b'$PIN', bcrypt.gensalt()).decode())")

# 5. Store hashed PIN securely
echo "$HASHED_PIN" > "$FILE"
chmod 600 "$FILE"

echo "✅ Hashed PIN stored in $FILE"