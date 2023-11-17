# Making plaquettes

Theere are a few points to consider when designing a tool:
- What is the scope?
  -  Applicability: only for the surface code or for generic stabilizer codes?
  -  Flexibility: assuming native connectivity between the physical qubits?
  - Scale: small prototype with ~10-30 stabilizers or with ~100-1000 stabilizers?
- Who will be the users?
  -Are they proficient with coding and/or math?

For example, considering the requirement of a tool for the surface code only,
on devices with native connectivity, targeting large-distance codes,
for users who are familiar with Python coding...
Then I would suggest a less visual approach to input the information.
For example, just providing a list of stabilizers to build the code.
Then the tool can automatically update the visualization.

Something in between could be a Python module with all relevant functions and
a small GUI to lower the barrier of adoption while providing intuitive confirmation
of the tool’s working.
