import arcpy, datetime

sdeWorkspace = r"\\networkPath\somefolder\sdeConnectionFileFromCatalog.sde" #you will typically find this at C:\Users\YourUserName\AppData\Roaming\Esri\Desktop10.8\ArcCatalog
gdbExport = r"\\Networkfolder\SomeProjectFolder\EmailNotificationForChanges.gdb"
compare_fileWaterValves = r"\\networkPath\somefolder\MapLayer1Compare.txt"
compare_fileSewerValves = r"\\networkPath\somefolder\MapLayer2Compare.txt"


arcpy.env.workspace = sdeWorkspace

arcpy.env.overwriteOutput = True

export_date = datetime.datetime.now().strftime("%Y%m%d")
yesterday_dateojb = datetime.datetime.now() - datetime.timedelta(days=1)
yesterday_date = yesterday_dateojb.strftime("%Y%m%d")


System_Valves_SewerDATE = "System_Valves_Sewer" + export_date
System_Valves_WaterDATE = "System_Valves_Water" + export_date


System_Valves_SewerYesterdayDATE = "System_Valves_Sewer" + yesterday_date
System_Valves_WaterYesterdayDATE = "System_Valves_Water" + yesterday_date


def deleteFC(fc):
    if arcpy.Exists(fc):
        print(f"{fc} exists, deleting...", end="")
        try:
            arcpy.management.Delete(fc)  #delete FEATURES isn't deleteFeatureCLASS... !!!!
            print("successful")
        except Exception as e:
            print(f"unable to delete, reason: {e}")
    else:
        print(f"{fc} doesn't exist, skipping...")

###  DELETE SECTION  look in local gdb and  System_Valves_WaterDATE and SewerDATE if they exist
###
###
###
###
arcpy.env.workspace = gdbExport


print("Workspace is....")
print(arcpy.env.workspace)

fdlist=arcpy.ListDatasets(feature_type='Feature')
print("fdlist local GDB: ")
print(fdlist)

print("begin deleting old data....")


fclist=arcpy.ListFeatureClasses() #no fd featuredataset defined so only select loose featureclasses not in datasets
print("fclist is....")
print(fclist)
for fc in fclist:
    print("begin sewer deleting old FC with todays date")
    print("fc in fclist is:")
    print(fc)
    if fc == System_Valves_SewerDATE:
        print("deleting " + fc)
        deleteFC(fc)
        print("Successfully deleted " + fc)

    else:
        pass  
    
for fc in fclist:
    print("begin water deleting old FC with todays date")
    if fc == System_Valves_WaterDATE:
        print("deleting " + fc)

        deleteFC(fc)
        print("Successfully deleted " + fc)
    else:
        pass     
    
print("printing fclist in local gdb again after deleting any featureclasses with today's date .....")
    
print(fclist)
##### 
####
###
###
###
###
#######  EXPORT SECTION ##########


arcpy.env.workspace = sdeWorkspace
print("begin exporting....")
print("switching back to SDE workspace: ")
print(arcpy.env.workspace)

fdlist=arcpy.ListDatasets(feature_type='Feature')
print("printing fdlist from SDE....")
print(fdlist)

######

for fd in fdlist:
        print("SDE fd: " + fd) 
        fclist=arcpy.ListFeatureClasses(feature_dataset=fd) #no fd featuredataset defined so only select loose featureclasses not in datasets
        print("SDE fclist: ")
        print(fclist)  
        for fc in fclist:    
            print("SDE fc: ")
            print(fc)
        if fd == "SOMEGISSDEDATABSE.DBO.WATER_ASSETS":   # works but not good logic, should look for fc name in ALL FD's, in case FD name changes, TO DO fix bug later so Dataset name not hard-coded
            arcpy.conversion.FeatureClassToGeodatabase("SOMEGISSDEDATABSE.DBO.System_Valves_Water", gdbExport)
            arcpy.env.workspace = gdbExport
            print("SDE fclist: ")
            print(fclist)   #
            print("SDE fc: ")
            print(fc)
            ######
            
       

        elif fd == "SOMEGISSDEDATABSE.DBO.SEWER_ASSETS":
            arcpy.env.workspace = sdeWorkspace
            arcpy.conversion.FeatureClassToGeodatabase("SOMEGISSDEDATABSE.DBO.System_Valves_Sewer", gdbExport)
            
           
        else:
            pass

        
        #####
        ######
        #   RENAME SECTION featureclasses in local gdb
        ###  note TO DO - API I guess doesn't change the attach and attachRel tables, they don't rename. But no need to worry about for this script purpose. ask solutions engineering at Esri UC
############
arcpy.env.workspace = gdbExport
print("switching back to local gdb workspace to rename layers and tack on Date: ")
print(arcpy.env.workspace)
fclist=arcpy.ListFeatureClasses() #no fd featuredataset defined so only select loose featureclasses not in datasets
print("local fclist: ")
print(fclist)
for fc in fclist:
    print("local for FC in FClist routine starting...")
    if fc == "System_Valves_Sewer":  
        print("renaming local fc:  " + fc)
        #
        arcpy.management.Rename("System_Valves_Sewer", System_Valves_SewerDATE)
    else:
        pass  
    
for fc in fclist:
    if fc == "System_Valves_Water":    
        print("renaming local fc: " + fc)
        arcpy.management.Rename("System_Valves_Water", System_Valves_WaterDATE)     
    else:
        pass     
    
print("final local fclist: ")
print(fclist)



#####
##########   compare water valves to see if they moved SECTION
#####


print("beginning water valve geometry compare....")
#could also use this https://community.esri.com/t5/arcgis-data-interoperability-blog/see-what-changed-and-where-it-changed/ba-p/883713

# Set local variables

base_features = gdbExport + "\\" + System_Valves_WaterYesterdayDATE    

test_features = gdbExport + "\\" + System_Valves_WaterDATE

sort_field = "OBJECTID"
#field in common with both datasets, primary key. Will use ObjectID but maybe will consider asssetID later 

compare_type = "GEOMETRY_ONLY"
ignore_option = "IGNORE_M;IGNORE_Z"
xy_tolerance = "0.001 FEET"  #or meters 
m_tolerance = 0
z_tolerance = 0

attribute_tolerance = ""
omit_field = "#"

continue_compare = "CONTINUE_COMPARE"
compare_file = compare_fileWaterValves
 
print("comparison set up... now writing WATER results....")
# Process: FeatureCompare GP Toolbox tool
compare_result = arcpy.FeatureCompare_management(
    base_features, test_features, sort_field, compare_type, ignore_option, 
    xy_tolerance, m_tolerance, z_tolerance, attribute_tolerance, omit_field, 
    continue_compare, compare_file)
print(compare_result[1])
print(arcpy.GetMessages())








#####
##########   compare Sewer valves to see if they moved SECTION
#####

print("beginning Sewer valve geometry compare....")



# Set local variables

base_features = gdbExport + "\\" + System_Valves_SewerYesterdayDATE    
#yesterday date stamp, supposedly correct data

test_features = gdbExport + "\\" + System_Valves_SewerDATE
#today date stamp points

sort_field = "OBJECTID"

compare_type = "GEOMETRY_ONLY"
ignore_option = "IGNORE_M;IGNORE_Z"
xy_tolerance = "0.001 FEET"  
m_tolerance = 0
z_tolerance = 0

attribute_tolerance = ""
omit_field = "#"

continue_compare = "CONTINUE_COMPARE"
compare_file = compare_fileSewerValves
print("comparison set up... now writing SEWER results....")

# Process: FeatureCompare
compare_result = arcpy.FeatureCompare_management(
    base_features, test_features, sort_field, compare_type, ignore_option, 
    xy_tolerance, m_tolerance, z_tolerance, attribute_tolerance, omit_field, 
    continue_compare, compare_file)
print(compare_result[1])
print(arcpy.GetMessages())




with open(compare_fileWaterValves) as f:
    datafileWater = f.readlines()

    

with open(compare_fileSewerValves) as f:
    datafileSewer = f.readlines()


def Watercheck():
    global foundWater  # global keyword sends it to global namespace,  refactor later
    foundWater = False
    for line in datafileWater:
        if 'Geometries are different' in line:
            foundWater = True


Watercheck()

if foundWater == True:
    print("Sewer geomety has changed - True")
    #refactor after i can log in w admin and install yagmail to send email
    
    # Email send SECTION # full credit to Denys and Veljko
    # https://mailtrap.io/blog/python-send-email-gmail/
    
    import smtplib
    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    sender_email = "sendera@gmail.com"
    sender_password = "16 digit Gmail code"   # NOTE you might want to store this in separate file or in system env - i will refactor for this later
    recipient_email = "youremail@email.com"
    subject = "System Water Valves have changes in geometry"
    body = "System Water Valves have changes in geometry"


    with open(compare_fileWaterValves, "rb") as attachment:
        # Add the attachment to the message
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
    "Content-Disposition",
    f"attachment; filename= 'WaterValvesCompare.txt'",
    )

    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = recipient_email
    html_part = MIMEText(body)
    message.attach(html_part)
    message.attach(part)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
       server.login(sender_email, sender_password)
       server.sendmail(sender_email, recipient_email, message.as_string())



    
else:
    print("False")












def Sewercheck():
    global foundSewer
    foundSewer = False
    for line in datafileSewer:
        if 'Geometries are different' in line:
            foundSewer = True


Sewercheck()

if foundSewer == True:
    print("Sewer geomety has changed - True")
    # yagmail to send email of file after refactor

    
    import smtplib
    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText


    sender_email = "sendera@gmail.com"
    sender_password = "16 digit Gmail code"   # NOTE you might want to store this in separate file or in system env - i will refactor for this later
    recipient_email = "youremail@email.com"
    subject = "System Water Valves have changes in geometry"
    body = "System Water Valves have changes in geometry"


    with open(compare_fileSewerValves, "rb") as attachment:
        # Add the attachment to the message
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
    "Content-Disposition",
    f"attachment; filename= 'SewerValvesCompare.txt'",
    )

    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = recipient_email
    html_part = MIMEText(body)
    message.attach(html_part)
    message.attach(part)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
       server.login(sender_email, sender_password)
       server.sendmail(sender_email, recipient_email, message.as_string())



    
else:
    print("False")


