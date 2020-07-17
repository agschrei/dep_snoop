# **py-dep-snoop**  
## the dependency analyzer you never knew you needed

The ultimate goal for this side-project is to provide the following functionality:
- [x] rich console output listing the packages installed in your (virtual) environment
- [ ] project Bill of Materials in JSON format w/ schema
- [ ] dependency tree that shows which first-level dependencies contribute which transitive dependencies
- [ ] statistics about your dependencies

At present we use 
```python
importlib.metadata.Distribution.discover()
```
to build a list of installed dependencies for the current environment, but ultimately we also want to support other query types,
like querying the dependency tree of a specific pypi package or egg  
[PEP-508](https://www.python.org/dev/peps/pep-0508/) provides great detail on how dependencies are specified in the various distribution formats
<br>

A current example of running the tool might look like this when running in a KDE Plasma Konsole  
![Demonstration](/doc/example.png)