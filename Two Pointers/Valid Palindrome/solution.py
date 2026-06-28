class Solution(object):
    def isPalindrome(self, s):
        """
        :type s: str
        :rtype: bool
        """
        final=''
        for le in s:
            if le.isalnum():
                final+=le.lower()
        if final[::-1] == final:
            return True
        return False
        