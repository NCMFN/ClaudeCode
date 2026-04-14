with open('final_colab_script.py', 'r') as f:
    lines = f.readlines()

with open('new_flowchart_logic.py', 'r') as f:
    new_logic = f.read()

start_idx = 1715 # zero-indexed line 1716
end_idx = 1840 # zero-indexed line 1841

final_lines = lines[:start_idx] + [new_logic + "\n"] + lines[end_idx:]
with open('final_colab_script.py', 'w') as f:
    f.writelines(final_lines)
print("Replaced.")
