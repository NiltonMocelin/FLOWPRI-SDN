declare -i number
# The script will treat subsequent occurrences of "number" as an integer.		

number=30000000
echo "Number = $number"     # Number = 3

number=three
echo "Number = $number"     # Number = 0
# Tries to evaluate the string "three" as an integer.wq

