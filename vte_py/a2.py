# [
# ]

#  # Create a new Engineering Data System and access Structural Steel
#
template1 = GetTemplate(TemplateName="EngData")
system1 = template1.CreateSystem()
engineeringData1 = system1.GetContainer(ComponentName="Engineering Data")
matl1 = engineeringData1.GetMaterial(Name="Structural Steel")
#
# Change the value of a simple single-valued property
#
matlProp1 = matl1.GetProperty(Name="Density")
matlProp1.SetData(Variables="Density",
                  Values="8500 [kg m^-3]")
#
# Set Temperature-dependent data for Elasticity based
# on lists of variables and values.
matlProp2 = matl1.GetProperty(Name="Elasticity")
temperature = ["400 [K]", "600 [K]", "800 [K]"]
E = ["2e5 [MPa]", "1.9e5 [MPa]", "1.6e5 [MPa]"]
matlProp2.SetData(Variables=["Temperature", "Young's Modulus"],
                  Values=[temperature, E])
#
# Change the Temperature for the second table entry.
#
matlProp2.SetData(Index=1,
                  Variables="Temperature",
                  Values="625 [K]")
#
# Set a list for Poisson's Ratio starting at the second table entry.
#
matlProp2.SetData(Index=1,
                  Variables="Poisson's Ratio",
                  Values=[0.3, 0.3])
#
# Set Temperature-dependent property data for the Coefficient of Thermal Expansion
# using a dictionary. The dictionary key is the Variable name,
# followed by the list of values for the variable.
#
matlProp3 = matl1.GetProperty(Name="Coefficient of Thermal Expansion")
newData = {"Temperature": ["200 [F]", "400 [F]", "600 [F]", "800 [F]", "1000 [F]"],
           "Coefficient of Thermal Expansion": ["6.3e-6 [F^-1]", "7.0e-6 [F^-1]",
                                                "7.46e-6 [F^-1]", "7.8e-6 [F^-1]",
                                                "8.04e-6 [F^-1]"]}
matlProp3.SetData(SheetName="Coefficient of Thermal Expansion",
                  SheetQualifiers={"Definition Method": "Secant", "Behavior": "Isotropic"},
                  Data=newData)
