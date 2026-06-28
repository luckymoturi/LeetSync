class Solution(object):
    def limitOccurrences(self, nums, k):
        """
        :type nums: List[int]
        :type k: int
        :rtype: List[int]
        """
        for i in range(len(nums)-1,-1,-1):
            c=0
            for j in range(i+1):
                if nums[i] == nums[j]:
                    c+=1
            if c>k:
                nums.pop(i)
        return nums

 


        