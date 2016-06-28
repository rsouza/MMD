https://github.com/jldbc/gunsandcrime

# Guns and Crime
##A replication of Marvell and Moody's experiment of impact of gun ownership on crime rates

Marvell and Moody's study takes gun ownership data and measures its effect on crime ownership from 1977 - 1998. I have replicated their data, adding rows for years 1999-2013, and run an updated study. 

Attached is the data set in .csv and .dta format, my team's write-up, and the STATA .do file for replicating the commands used.

This data is collected from public sources, so feel free to use and improve upon it as you please. 

###The data set includes:

####Crime Variables:
**murder:** murders per million population

**rape:** rapes per million population

**robbery:** robberies per million population

**burglary:** burglaries per million population 

**assault:** assaults per million population

**majorcrime:** total major crime per million population

[crime measurements all from FBI Uniform Crime Report]  

####Gun Ownership Variables:
**pgs:** pct. of suicides by gun (proxy for gun ownership) 

**hg:** pct. households owning handguns according to General Social Survey (better data than Gallup poll)

**phg:** imputed handgun measurement. Uses linear model to predit years when GSS did not ask this question.

**gun:** pct. households owning guns of any kind according to GSS

**pgun:** imputed gun, measured similarly to phg. 

**domestic_gun:** guns available for sale in the US (a proxy - gun production - gun exports)

**gallup_owngun:** pct. households saying they own 1+ gun(s) in gallup polls

**gunsamm:** Guns and Ammo magazine circulation

**amrmms:** American Rifleman magazine circulation

**amhmms:** American Hunter magazine circulation

[gun measurements from GSS, CDC Wonder, Bureau of Alcohol, Tobacco, Firearms and Explosives, Gallup, and Alliance for Audited Media]

**note:** I could only find magazine data from 1999-2013. Duggan (2001) uses these as a proxy for gun ownership in the US. I believe this is a weak proxy, but I included what I could in order to attempt to test it. 


####Control Varbables: 
**Year:** range 1980-2013

**Pop:** population in thousands 

**ampct:** percentage population african american 

**metpct:** percent of population living in urban areas 

**unrate:** averge unemployment by year 

**prison:** scaled prison population

**employ:** pct. population on standard payroll employment (nonfarm)

**military:** employed military personnel 

**rpci:** real per capita income 

**r1524:** pct. population age 15-24

**r2544:** pct. population age 25-44

**r4564:** pct. population age 45-64
