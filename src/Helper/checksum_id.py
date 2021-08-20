
def checksum_id(id):
    try:
        if len(id) != 17:
            return False
        id = id.replace("-", "")
        id = list(id)
        check_digit = int(id.pop(12))
        sum = 0
        count = 2
        for i in reversed(id):
            i = int(i)
            sum += count*i
            count += 1
        sum = sum % 11
        sum = 11 - sum
        sum = sum % 10
        
        if sum == check_digit:
            return True
        else: return False
    except Exception as e:
        print(e)
        return False
