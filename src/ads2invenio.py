'''
Main module

I parse the parameters

I check the situation of the latest extraction
if the latest extraction is ok or if there is no extraction I run a new complete extraction (that can be full or an update)
if the last extraction failed, I start again where I stopped the last time

if there has to be a new extraction, I create a new folder with the new three files:
1- the bibcodes to parse
2- the parsed bibcodes
3- the bibcodes that gave problems during the extraction
then I write the bibcodes to extract in the proper file

Finally I lunch the manager with the entire list of bibcodes to extract

'''

