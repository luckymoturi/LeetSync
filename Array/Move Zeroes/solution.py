class Solution(object):
    def moveZeroes(self, nums):
        count = nums.count(0)

        for _ in range(count):
            nums.remove(0)
            nums.append(0)

        print(nums)