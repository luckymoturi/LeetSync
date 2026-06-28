# Definition for singly-linked list.
# class ListNode(object):
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution(object):
    def middleNode(self, head):
        """
        :type head: Optional[ListNode]
        :rtype: Optional[ListNode]
        """
        slow,fast=head,head
        while fast and fast.next:
            slow=slow.next
            fast=fast.next.next
        return slow

       
        # if not head or not head.next:
        #    return head

        # stack = []
        # while head:
        #    stack.append(head.val)
        #    head = head.next

        #    if len(stack)>0 :
        #     n= len(stack)/2
        #     return stack[n]
        # return None
        
            
            

       
      
        
        
        

        
        