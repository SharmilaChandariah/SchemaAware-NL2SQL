
# Sample Output

Input:
Find policies with no driver

Output:
SELECT policy_id
FROM policy_period
WHERE policy_id NOT IN (
    SELECT policy_id FROM driver
);
