# get all the asset names
"""
MainLine
ServiceLine
AddressPoint
Mapsheet
BusinessDistrict
Proposed
Riser
Stub
PropertyLine
ROWLine
MobileHomeParks
ControllableFitting
CPTestPoint
GasLeakRepair
GasValve
HouseNbrAnno
NonControllableFitting
RegulatorStation
FOMS_AC_Data
LandbaseText_Addr
"""
def getAssetsName():
    query = f""" 
        SELECT * from dbo.LUTAssetTypes 
    """
    return query


def getQueryStrCoveredAssets(survey_id, mapsheet_id):
    # You'll use INNER JOIN when you want to return only records having pair on both sides
    # You'll use LEFT JOIN when you need all records from the “left” table, no matter if they have pair in the “right” table or not
    # Outer joins such as left join preserve rows that don't match

    query = f""" 
        DECLARE @SID INT = {survey_id}
        DECLARE @mapsheet INT = {mapsheet_id}
        SELECT
            SurveyId
            ,SurveyName
            ,[Date]
            ,Technician
            ,DeviceSerialNumber
            ,MapsheetId
            ,Atlas
            ,WorkOrder
            ,AssetType  
            ,CASE
                WHEN t.SurveyType =  '1' THEN 'Atmospheric Corrosion'
                WHEN t.SurveyType =  '2' THEN 'Inside Meter'
                WHEN t.SurveyType =  '3' THEN 'Bridge Crossing'
                WHEN t.SurveyType =  '4' THEN 'High Occupamncy Building'
                WHEN t.SurveyType =  '5' THEN 'Public Building'
                WHEN t.SurveyType =  '6' THEN 'Business District'
                WHEN t.SurveyType =  '7' THEN 'Residential'
                WHEN t.SurveyType =  '8' THEN 'Transmission Patrol'
                WHEN t.SurveyType =  '9' THEN 'Transmission Leak Survey'
                WHEN t.SurveyType = '10' THEN 'Cast Iron Frost Patrol'
                WHEN t.SurveyType = '11' THEN 'Farm Tap'
                WHEN t.SurveyType = '12' THEN 'Natural Disaster Patrol'
                WHEN t.SurveyType = '13' THEN 'Overpressurization'
                WHEN t.SurveyType = '14' THEN 'Prepave'
                ELSE 'InvalidSurveyTypeCode'
                END AS SurveyType
            ,CASE
                WHEN t.Status =  '1' THEN 'Ready'
                WHEN t.Status =  '2' THEN 'In Progress'
                WHEN t.Status =  '3' THEN 'Completed'
                WHEN t.Status =  '4' THEN 'Closed'
                WHEN t.Status =  '5' THEN 'Live Survey'
                WHEN t.Status =  '6' THEN 'Published Survey'
                WHEN t.Status =  '7' THEN 'Reopened'
                ELSE 'InvalidStatusCode'
                END AS MapsheetStatus
            ,CONVERT(INT, IsCovered) AS IsCovered
            ,CONVERT(INT, IsApproved) AS IsApproved
            ,AssetGeometry
            ,CustomerId
            FROM (    
                SELECT  m.WorkOrderNumber as WorkOrder
                        ,m.LegacyMapsheetId  as MapsheetId
                        ,m.MapsheetName as Atlas
                        ,m.CustomerId
                        ,astat.WhenCompleted as Date
                        ,astat.IsCovered
                        ,astat.IsApproved
                        ,astat.AssetType as AssetType
                        ,a.FirstName + ' ' + a.LastName Technician   
                        ,s.Id as SurveyId
                        ,s.SurveyType as SurveyType
                        ,s.SurveyName as SurveyName
                        ,m.MapsheetStatus as Status
                        ,astat.DeviceSerialNumber as DeviceSerialNumber
                        ,astat.AssetGeometry.ToString() as AssetGeometry
                    FROM SbuSurvey s
                    INNER JOIN Mapsheets m    ON m.SurveyId = s.Id
                    INNER JOIN AssetCoverageStatus_{survey_id} astat ON astat.MapSheetId = m.LegacyMapsheetId 
                    INNER JOIN AspNetUsers a ON a.Id = astat.CompletedBy AND astat.IsCovered = 1

                WHERE s.Id = @SID AND astat.MapsheetId = @mapsheet AND astat.IsCovered = 1
                
                GROUP BY astat.WhenCompleted, a.FirstName + ' ' + a.LastName, 
                        astat.DeviceSerialNumber, astat.IsCovered, astat.IsApproved, m.WorkOrderNumber,
                        m.SurveyId, s.Id,  m.LegacyMapsheetId, m.MapsheetName, s.SurveyType, s.SurveyName, 
                        astat.AssetType, m.MapsheetStatus, m.CustomerId,
                        astat.AssetGeometry.ToString()
            ) t

        ORDER BY [Date], Technician, DeviceSerialNumber, WorkOrder, MapsheetId, SurveyName, SurveyId, SurveyType, MapsheetStatus
        """  
    return query            


def GetClosedOrCompletedMapsheetsForASurvey_sp():
    # this is how a stored procedure looks like when created, remove the triple quotes and enter into database
    store_procedure = """\
    SET ANSI_NULLS ON
    GO
    SET QUOTED_IDENTIFIER ON
    GO

    ALTER PROC [dbo].[GetClosedOrCompletedMapsheetsForASurvey] (@SurveyId INT, @AssetType tinyint, @MapSheetStatus tinyint)
    AS
    BEGIN
        DECLARE
        @AssetCoverageStatusTable NVARCHAR(128),
        @sql NVARCHAR(MAX);

    SET @AssetCoverageStatusTable = N'AssetCoverageStatus_' + CAST(@SurveyId AS VARCHAR(10)) + '';
    SET @sql = N'SELECT
       CONVERT(DATE,WhenCompleted) [Completed Date], m.WorkorderNumber as [Workorder #], MapSheetId as Atlas,
       (a.FirstName +'', ''+ a.LastName) as [Technician Name], 
       SegmentLengthInFeet as [Length in Feet], 
       DeviceSerialNumber as [Serial Number]

    FROM '+ @AssetCoverageStatusTable +' astat
    INNER JOIN AspNetUsers a ON a.Id = astat.CompletedBy
    INNER JOIN Mapsheets m ON m.LegacyMapsheetId = astat.MapSheetId
    WHERE AssetType = '+ CAST(@AssetType AS VARCHAR(10)) +'
    AND MapSheetId IN
       (
        SELECT DISTINCT m.LegacyMapsheetId FROM SbuSurvey s
        INNER JOIN Mapsheets m ON m.SurveyId = s.Id
        WHERE s.Id = '+ CAST(@SurveyId AS VARCHAR(10)) +'   AND m.MapsheetStatus = '+ CAST(@MapSheetStatus AS VARCHAR(10)) +'
       )
    Order by CONVERT(DATE,WhenCompleted) ASC, MapsheetId, [Technician Name] ASC
    ';
    EXEC sp_executesql @sql;
    END
    """


def getQueryStrMapsheet(mapsheet_id):

    return f""" 
        DECLARE @mapsheet INT = {mapsheet_id}

        SELECT ssm.Id, ssm.SurveyId, ss.SurveyName, ssm.LegacyMapsheetId, ssm.WorkOrderNumber, 
               ssm.MapsheetGeom.ToString() MapsheetGeom
        FROM Mapsheets ssm
        JOIN SbuSurvey ss ON ssm.SurveyId = ss.Id
        WHERE ssm.LegacyMapsheetId = @mapsheet
        ORDER BY ssm.WorkOrderNumber
        """


def getQueryStrNotCoveredAssets(survey_id, mapsheet_id):
    # this lacks Technician to get not covered.

    return f""" 
    DECLARE @mapsheet INT = {mapsheet_id}
    DECLARE @surveyId INT = {survey_id}

    SELECT
        SurveyId
        ,SurveyName
        ,[Date]
        ,DeviceSerialNumber
        ,MapsheetId
        ,Atlas
        ,WorkOrder
        ,AssetType  
        ,CASE
            WHEN t.SurveyType =  '1' THEN 'Atmospheric Corrosion'
            WHEN t.SurveyType =  '2' THEN 'Inside Meter'
            WHEN t.SurveyType =  '3' THEN 'Bridge Crossing'
            WHEN t.SurveyType =  '4' THEN 'High Occupamncy Building'
            WHEN t.SurveyType =  '5' THEN 'Public Building'
            WHEN t.SurveyType =  '6' THEN 'Business District'
            WHEN t.SurveyType =  '7' THEN 'Residential'
            WHEN t.SurveyType =  '8' THEN 'Transmission Patrol'
            WHEN t.SurveyType =  '9' THEN 'Transmission Leak Survey'
            WHEN t.SurveyType = '10' THEN 'Cast Iron Frost Patrol'
            WHEN t.SurveyType = '11' THEN 'Farm Tap'
            WHEN t.SurveyType = '12' THEN 'Natural Disaster Patrol'
            WHEN t.SurveyType = '13' THEN 'Overpressurization'
            WHEN t.SurveyType = '14' THEN 'Prepave'
            ELSE 'InvalidSurveyTypeCode'
            END AS SurveyType
        ,CASE
            WHEN t.Status =  '1' THEN 'Ready'
            WHEN t.Status =  '2' THEN 'In Progress'
            WHEN t.Status =  '3' THEN 'Completed'
            WHEN t.Status =  '4' THEN 'Closed'
            WHEN t.Status =  '5' THEN 'Live Survey'
            WHEN t.Status =  '6' THEN 'Published Survey'
            WHEN t.Status =  '7' THEN 'Reopened'
            ELSE 'InvalidStatusCode'
            END AS MapsheetStatus
        ,CONVERT(INT, IsCovered) AS IsCovered
        ,CONVERT(INT, IsApproved) AS IsApproved
        ,AssetGeometry
        ,CustomerId
        FROM (    
            SELECT  m.WorkOrderNumber as WorkOrder
                    ,m.LegacyMapsheetId  as MapsheetId
                    ,m.MapsheetName as Atlas
                    ,m.CustomerId
                    ,astat.WhenCompleted as Date
                    ,astat.IsCovered
                    ,astat.IsApproved
                    ,astat.AssetType as AssetType 
                    ,s.Id as SurveyId
                    ,s.SurveyType as SurveyType
                    ,s.SurveyName as SurveyName
                    ,m.MapsheetStatus as Status
                    ,astat.DeviceSerialNumber as DeviceSerialNumber
                    ,astat.AssetGeometry.ToString() as AssetGeometry
                FROM SbuSurvey s
                INNER JOIN Mapsheets m    ON m.SurveyId = s.Id
                INNER JOIN AssetCoverageStatus_{survey_id} astat ON astat.MapSheetId = m.LegacyMapsheetId 

            WHERE s.Id = @surveyId AND astat.MapsheetId = @mapsheet AND astat.IsCovered = 0
            
            GROUP BY astat.WhenCompleted, 
                    astat.DeviceSerialNumber, astat.IsCovered, astat.IsApproved, m.WorkOrderNumber,
                    m.SurveyId, s.Id,  m.LegacyMapsheetId, m.MapsheetName, s.SurveyType, s.SurveyName, 
                    astat.AssetType, m.MapsheetStatus, m.CustomerId,
                    astat.AssetGeometry.ToString()
        ) t

    ORDER BY [Date], DeviceSerialNumber, WorkOrder, MapsheetId, SurveyName, SurveyId, SurveyType, MapsheetStatus
"""

def getCGIsBySurveyIdForAMapsheet_test(survey_id, mapsheet_id, org_id):
    
    return f""" 
    DECLARE @CUSTID INT = {org_id}
    DECLARE @SID INT = {survey_id}
    DECLARE @MPSID INT = {mapsheet_id}

    SELECT 
        S.SurveyName
        ,FD.Timestamp 
        ,A.FirstName + ' ' + A.LastName as Technician
        ,O.Id as Organization 
        ,M.LegacyMapsheetId Atlas 
        ,M.WorkOrderNumber WorkOrder
        ,'   ' Address
        -- ,FD.Attempt
        ,CASE
            WHEN FD.Attempt = 4 THEN 'Completed'
            WHEN FD.Attempt = 5 THEN 'Rejected'
            WHEN FD.Attempt > 0 AND FD.Attempt < 4 THEN CONCAT(TRIM(STR(FD.Attempt)), ' Attempt')
            ELSE CONCAT('InvalidAttemptCode ', TRIM(STR(FD.Attempt)))
        END AS AttemptStatus
        ,'CGI' Reason
        ,CASE
            WHEN FD.FormType =  '0' THEN 'None'
            WHEN FD.FormType =  '1' THEN 'Leak'
            WHEN FD.FormType =  '2' THEN 'Leak Indication'
            WHEN FD.FormType =  '3' THEN 'AOC'
            WHEN FD.FormType =  '4' THEN '(UOC) Safety Issue'
            WHEN FD.FormType =  '5' THEN 'CGI (Can''t Get In)'
            WHEN FD.FormType =  '6' THEN 'Leak Reminder'
            WHEN FD.FormType =  '7' THEN 'Incorrect Data'
            WHEN FD.FormType =  '8' THEN 'Billable Item'
            WHEN FD.FormType =  '9' THEN 'Meter Inspection'
            WHEN FD.FormType = '10' THEN 'Atmospheric Corrosion'
            WHEN FD.FormType = '11' THEN 'Audit Form'
            ELSE 'InvalidFormTypeCode'
        END AS FormType
        -- these are in the sample spreadsheet (requirements) that is currently missing from this query. TODO
        -- Comments, Appointment, Tagged, MeterNumber, Abandoned WR#, PdfFiles(a pulldown), SurveyAttachments(pulldown), 
        -- SurveyAttachements1(pulldown), SurveyAttachments2(pulldown), ProjectId, Apt. or Space#
        -- [Select All, Click, Blanks] 
        ,FD.PdfFileName as PdfFiles
        ,ROUND(FD.Latitude ,6) Latitude
        ,ROUND(FD.Longitude,6) Longitude
        ,CASE
            WHEN FD.Status =  '1' THEN 'Ready'
            WHEN FD.Status =  '2' THEN 'In Progress'
            WHEN FD.Status =  '3' THEN 'Completed'
            WHEN FD.Status =  '4' THEN 'Closed'
            WHEN FD.Status =  '5' THEN 'Live Survey'
            WHEN FD.Status =  '6' THEN 'Published Survey'
            WHEN FD.Status =  '7' THEN 'Reopened'
            ELSE 'InvalidStatusCode'
        END AS SurveyStatus
        ,CAST(FD.Status AS varchar) Status
        ,FD.UniqueId
        ,FD.LinkedId
        ,FD.ContainerName
        ,FD.CreatedDate
        ,FD.UpdatedDate
    FROM SbuFormDetails FD  
        INNER JOIN SbuSurvey S ON S.Id = FD.RefId
        INNER JOIN AspNetUsers A ON A.Id = FD.TechnicianId
        LEFT JOIN MapSheets M ON M.LegacyMapsheetId = FD.SbuSurveyMapSheetId
        LEFT  JOIN CustomerOrganisation O ON O.Id = S.CustomerOrganisationId

    WHERE FD.FormType = 5
    AND   S.CustomerOrganisationId = @CUSTID
    -- AND   M.LegacyMapsheetId = @MPSID 
    AND   FD.RefId = @SID

    ORDER BY SurveyName, 
        FD.Timestamp, 
        Technician,
        Atlas, 
        WorkOrder,
        FD.Attempt,
        FD.LinkedId, 
        FD.UniqueId    
    """


def getCGIsBySurveyIdForAMapsheet(survey_id, mapsheet_id, org_id):
    # public enum FieldType from DataFormField Table
    # {
    #     [Display(Name = "Text Input")]
    #     TextInput = 1,
    #     [Display(Name = "Dropdown")]
    #     Dropdown = 2,
    #     [Display(Name = "Radio Button")]
    #     RadioButton = 3,
    #     [Display(Name = "Attachment")]
    #     FileUpload = 4,
    #     [Display(Name = "Address")]
    #     Address = 5,
    #     [Display(Name = "Checkbox")]
    #     Checkbox = 6,
    #     [Display(Name = "Date Input")]
    #     Date = 7
    # }

    # public enum FormType from DataFormField Table
    # {
    #     [Display(Name = "None")]
    #     None = 0,
    #     [Display(Name = "Leak")]
    #     Leak = 1,
    #     [Display(Name = "Leak Indication")]
    #     LeakIndication = 2,  in dbo.SbuFormReadings
    #     [Display(Name = "AOC")]
    #     AOC = 3,
    #     [Display(Name = "Safety Issue")]
    #     SafetyIssue = 4,
    #     [Display(Name = "CGI (Can't Get In)")]
    #     NoAccess = 5,
    #     [Display(Name = "Leak Reminder")]
    #     LeakReminder = 6,
    #     [Display(Name = "Incorrect Data")]
    #     IncorrectData = 7,
    #     [Display(Name = "Billable Item")]
    #     Billing = 8,
    #     [Display(Name = "Meter Inspection")]
    #     MeterInspection = 9,
    #     [Display(Name = "Atmospheric corrosion")]
    #     AtmospheriCorrosion = 10,
    #     [Display(Name = "Audit Form")]
    #     AuditForm = 11
    # }

    reason_sql = """  (SELECT result.Reason FROM
                    (
                        SELECT SFD.Id AS SbuFormDetailsId,  
                            SFD.UniqueId, 
                            SFD.FormType, 
                            SSM.MapsheetName, 
                            SSM.WorkOrderNumber,
                            DFF.Label, 
                            DFF.FieldType, 
                            ISNULL(SSM.MapsheetName, ISNULL(DFFV.Value, SFV.Value)) as Reason 
                        FROM SbuFormFieldValue SFV
                        INNER JOIN DataFormFields DFF ON SFV.FieldId = DFF.Id
                        INNER JOIN SbuFormDetails SFD ON SFV.SbuFormDetailId = SFD.Id
                        LEFT JOIN DataFormFieldValues DFFV ON DFFV.Id LIKE SFV.Value
                        LEFT JOIN SbuSurveyMapsheet SSM ON SSM.SbuSurveyId = SFD.RefId AND SSM.Id LIKE SFV.Value
                        WHERE IsAuditData = 0 AND IsReworkData = 0 AND DFF.FieldType NOT IN (4, 6) 
                              AND SFD.FormType = 5 AND Label LIKE '%Reason%'
                    ) AS result
                    WHERE result.SbuFormDetailsId = FD.Id
                )
    """
    address_sql = """ (SELECT result.Address FROM
                    (
                        SELECT SFD.Id AS SbuFormDetailsId,  
                            SFD.UniqueId, 
                            SFD.FormType, 
                            SSM.MapsheetName, 
                            SSM.WorkOrderNumber,
                            DFF.Label, 
                            DFF.FieldType, 
                            ISNULL(SSM.MapsheetName, ISNULL(DFFV.Value, SFV.Value)) as Address 
                        FROM SbuFormFieldValue SFV
                        INNER JOIN DataFormFields DFF ON SFV.FieldId = DFF.Id
                        INNER JOIN SbuFormDetails SFD ON SFV.SbuFormDetailId = SFD.Id
                        LEFT JOIN DataFormFieldValues DFFV ON DFFV.Id LIKE SFV.Value
                        LEFT JOIN SbuSurveyMapsheet SSM ON SSM.SbuSurveyId = SFD.RefId AND SSM.Id LIKE SFV.Value
                        WHERE IsAuditData = 0 AND IsReworkData = 0 AND DFF.FieldType NOT IN (4, 6) 
                              AND SFD.FormType = 5 AND Label LIKE '%Address%'
                    ) AS result
                    WHERE result.SbuFormDetailsId = FD.Id
                )
    """
    return f"""
    DECLARE @CUSTID INT = {org_id} 
    DECLARE @SID INT = {survey_id}
    DECLARE @MPSID INT = {mapsheet_id}

    SELECT  S.SurveyName
            ,FD.Timestamp
            ,A.FirstName + ' ' + A.LastName Technician
            ,M.MapsheetName Atlas
            ,M.WorkOrderNumber WorkOrder
            ,{address_sql} Address
            ,FD.Attempt
            ,CASE
                WHEN FD.Attempt = 4 THEN 'Completed'
                WHEN FD.Attempt = 5 THEN 'Rejected'
                WHEN FD.Attempt > 0 AND FD.Attempt < 4 THEN CONCAT(TRIM(STR(FD.Attempt)), ' attempt made')
                ELSE CONCAT('InvalidAttemptCode ',TRIM(STR(FD.Attempt)))
            END AS AttemptStatus
            ,{reason_sql} Reason
            ,CASE
                WHEN FD.FormType =  '0' THEN 'None'
                WHEN FD.FormType =  '1' THEN 'Leak'
                WHEN FD.FormType =  '2' THEN 'Leak Indication'
                WHEN FD.FormType =  '3' THEN 'AOC'
                WHEN FD.FormType =  '4' THEN '(UOC) Safety Issue'
                WHEN FD.FormType =  '5' THEN 'CGI (Can''t Get In)'
                WHEN FD.FormType =  '6' THEN 'Leak Reminder'
                WHEN FD.FormType =  '7' THEN 'Incorrect Data'
                WHEN FD.FormType =  '8' THEN 'Billable Item' 
                WHEN FD.FormType =  '9' THEN 'Meter Inspection'
                WHEN FD.FormType = '10' THEN 'Atmospheric Corrosion'
                WHEN FD.FormType = '11' THEN 'Audit Form'
                ELSE 'InvalidFormTypeCode'
            END AS FormType
            -- these are in the sample spreadsheet (requirements) that is currently missing from this query. TODO
            -- Comments, Appointment, Tagged, MeterNumber, Abandoned WR#, PdfFiles(a pulldown), SurveyAttachments(pulldown), 
            -- SurveyAttachements1(pulldown), SurveyAttachments2(pulldown), ProjectId, Apt. or Space#
            -- [Select All, Click, Blanks] 
            ,FD.PdfFileName as PdfFiles
            ,ROUND(FD.Latitude ,6) Latitude
            ,ROUND(FD.Longitude,6) Longitude
            ,OrganisationName as Organization
            ,CASE
                WHEN FD.Status =  '1' THEN 'Ready'
                WHEN FD.Status =  '2' THEN 'In Progress'
                WHEN FD.Status =  '3' THEN 'Completed'
                WHEN FD.Status =  '4' THEN 'Closed'
                WHEN FD.Status =  '5' THEN 'Live Survey'
                WHEN FD.Status =  '6' THEN 'Published Survey'
                WHEN FD.Status =  '7' THEN 'Reopened'
                ELSE 'InvalidStatusCode'
            END AS SurveyStatus
            -- ,CAST(FD.Status AS varchar) Status
            ,FD.UniqueId
            ,FD.LinkedId
            ,FD.ContainerName
            ,FD.CreatedDate
            ,FD.UpdatedDate
    FROM    SbuFormDetails FD
            INNER JOIN SbuSurvey S            ON S.Id = FD.RefId
			INNER JOIN AspNetUsers A          ON A.Id = FD.TechnicianId
	        LEFT  JOIN SbuSurveyMapsheet M    ON M.Id = FD.SbuSurveyMapSheetId
            LEFT  JOIN CustomerOrganisation O ON O.Id = S.CustomerOrganisationId

    WHERE   FD.FormType = 5
    AND     S.CustomerOrganisationId = @CUSTID
    AND     M.Id = @MPSID AND FD.RefId = @SID
       

    ORDER BY SurveyName, 
    FD.Timestamp, 
    Technician,
    Atlas, 
    WorkOrder,
    FD.Attempt,
    FD.LinkedId, 
    FD.UniqueId
    """

def getLeak(survey_id, mapsheet_id, org_id, labels):
    return f"""
    DECLARE @CUSTID INT = {org_id} 
    DECLARE @SID INT = {survey_id}
    DECLARE @MPSID INT = {mapsheet_id}

    -- [Apt/Sp. #],[Meter Number],[Comments],[SWG Truck #],[ICS Implemented Time], [ICS Transferred to SWG Time]
    -- 34   1973    112044

    SELECT * FROM (
        select A.FirstName + ' ' + A.LastName as Technician
            ,SSM.MapsheetName as Atlas
            ,SSM.WorkOrderNumber as WorkOrder
            ,SFD.Timestamp
            ,SFD.UniqueId
            ,SFD.LinkedId
            ,SFD.Latitude
            ,SFD.Longitude
            ,S.Status SurveyStatus
            ,S.SurveyName
            ,O.ProjectName
            ,O.OrganisationName as OrganizationName
            ,SFD.Status as FormStatus
            ,SFV.Value [Value]
            ,DFF.Label [Label]
            ,DFF.FieldType
            ,DFF.FormType
            ,SFD.PdfFileName as [Pdf-files]
        from dbo.SbuFormDetails SFD
            INNER JOIN SbuSurvey S ON S.Id = SFD.RefId
            INNER JOIN AspNetUsers A ON A.Id = SFD.TechnicianId
            INNER JOIN SbuSurveyMapsheet SSM ON SSM.Id = SFD.SbuSurveyMapSheetId
            INNER JOIN SbuFormFieldValue SFV ON SFV.SbuFormDetailId = SFD.Id
            INNER JOIN DataFormFields DFF ON DFF.Id = SFV.FieldId
            INNER JOIN CustomerOrganisation O ON O.Id = DFF.CustomerOrganisationId
        where SFD.RefId = 1973 AND  DFF.FormType IN (1, 2, 6) AND
            SFD.SbuSurveyMapSheetId = 112044 AND DFF.FieldType = 1
            AND DFF.CustomerOrganisationId = 34
        -- Order by SurveyName, Atlas, WorkOrder, Timestamp, Technician, UniqueId, LinkedId
    ) AS T
    PIVOT (MAX([Value])
        FOR [Label] IN ({labels})
    ) AS P;
    """

def GetLeakReportColumns(survey_id, mapsheet_id, org_id):
    return f"""
    DECLARE 
    @SurveyId       INT = {survey_id}, 
	@MapSheetId     INT = {mapsheet_id},
    @CustomerId     INT = {org_id},
    @ColumnsToPivot NVARCHAR(255) = ''
  
    -- select the category names
    SELECT
        @ColumnsToPivot+=QUOTENAME(l.Label) + ','
    FROM (
            select DISTINCT DFF.Label
            from SbuFormDetails SFD
            INNER JOIN SbuFormFieldValue SFV ON SFV.SbuFormDetailId = SFD.Id
            INNER JOIN DataFormFields DFF ON DFF.Id = SFV.FieldId
            LEFT JOIN CustomerOrganisation O ON O.Id = DFF.CustomerOrganisationId
            where SFD.RefId = @SurveyId 
            AND   DFF.FormType IN (1, 2, 6) 
            AND   SFD.SbuSurveyMapSheetId = @MapSheetId 
            AND   DFF.FieldType = 1
            AND   DFF.CustomerOrganisationId = @CustomerId
    ) as l

    -- remove the last comma
    SET @ColumnsToPivot = LEFT(@ColumnsToPivot, LEN(@ColumnsToPivot) - 1);
    PRINT @ColumnsToPivot
    """

def GetLeakReport(survey_id, mapsheet_id, org_id):
    return f"""
    DECLARE 
    @SurveyId       INT = {survey_id}, 
	@MapSheetId     INT = {mapsheet_id},
    @CustomerId     INT = {org_id},
    @ColumnsToPivot NVARCHAR(255) = '',
    @sql            NVARCHAR(MAX) = ''

    -- select the category names
    SELECT 
        @ColumnsToPivot+=QUOTENAME(l.Label) + ','
    FROM (
        select DISTINCT DFF.Label
        from SbuFormDetails SFD
            INNER JOIN SbuFormFieldValue SFV ON SFV.SbuFormDetailId = SFD.Id
            INNER JOIN DataFormFields DFF ON DFF.Id = SFV.FieldId
            LEFT JOIN CustomerOrganisation O ON O.Id = DFF.CustomerOrganisationId
        where SFD.RefId = @SurveyId 
            AND  DFF.FormType IN (1, 2, 6) 
            AND SFD.SbuSurveyMapSheetId = @MapSheetId 
            AND DFF.FieldType = 1
            AND DFF.CustomerOrganisationId = @CustomerId
    ) as l
    ORDER BY 
        l.Label;

    -- remove the last comma
    SET @ColumnsToPivot = LEFT(@ColumnsToPivot, LEN(@ColumnsToPivot) - 1);
    PRINT @ColumnsToPivot

    -- construct dynamic SQL
    SET @sql ='
    SELECT * FROM (
        select (A.FirstName +'', ''+ A.LastName) as Technician
            ,SSM.MapsheetName as Atlas
            ,SSM.WorkOrderNumber as WorkOrder
            ,SFD.Timestamp
            ,SFD.UniqueId
            ,SFD.LinkedId
            ,SFD.Latitude
            ,SFD.Longitude
            ,S.Status SurveyStatus
            ,S.SurveyName
            ,O.ProjectName
            ,O.OrganisationName as OrganizationName
            ,SFD.Status as FormStatus
            ,SFV.Value [Value]
            ,DFF.Label [Label]
            ,DFF.FieldType
            ,DFF.FormType
            ,SFD.PdfFileName as [Pdf-files]
        from dbo.SbuFormDetails SFD
            INNER JOIN SbuSurvey S ON S.Id = SFD.RefId
            INNER JOIN AspNetUsers A ON A.Id = SFD.TechnicianId
            INNER JOIN SbuSurveyMapsheet SSM ON SSM.Id = SFD.SbuSurveyMapSheetId
            INNER JOIN SbuFormFieldValue SFV ON SFV.SbuFormDetailId = SFD.Id
            INNER JOIN DataFormFields DFF ON DFF.Id = SFV.FieldId
            INNER JOIN CustomerOrganisation O ON O.Id = DFF.CustomerOrganisationId
        where SFD.RefId = '+ CAST(@SurveyId AS VARCHAR(10)) +' 
            AND  DFF.FormType IN (1, 2, 6) 
            AND  SFD.SbuSurveyMapSheetId = '+ CAST(@MapSheetId AS VARCHAR(10)) +' 
            AND DFF.FieldType = 1
            AND DFF.CustomerOrganisationId = '+ CAST(@CustomerId AS VARCHAR(10)) +'
            --Order by SurveyName, Atlas, WorkOrder, Timestamp, Technician, UniqueId, LinkedId
    ) AS T
    PIVOT(
        MAX([Value]) 
        FOR [Label] IN ('+ @ColumnsToPivot +')
    ) AS P;'

    -- execute the dynamic SQL
    -- EXEC sp_executesql @sql;
    """


def getLeakReportValues(survey_id, mapsheet_id, org_id):
    return f"""
    DECLARE @CUSTID INT = {org_id} 
    DECLARE @SID INT = {survey_id}
    DECLARE @MPSID INT = {mapsheet_id}

    SELECT * FROM (
        select 
            SFV.Value [Value]
        from dbo.SbuFormDetails SFD
            INNER JOIN SbuSurvey S ON S.Id = SFD.RefId
            INNER JOIN AspNetUsers A ON A.Id = SFD.TechnicianId
            INNER JOIN SbuSurveyMapsheet SSM ON SSM.Id = SFD.SbuSurveyMapSheetId
            INNER JOIN SbuFormFieldValue SFV ON SFV.SbuFormDetailId = SFD.Id
            INNER JOIN DataFormFields DFF ON DFF.Id = SFV.FieldId
            INNER JOIN CustomerOrganisation O ON O.Id = DFF.CustomerOrganisationId
        where SFD.RefId = @SID AND  DFF.FormType IN (1, 2, 6) AND
            SFD.SbuSurveyMapSheetId = @MPSID AND DFF.FieldType = 1
            AND DFF.CustomerOrganisationId = @CUSTID
    ) AS T
    """

def getLeakColumns(survey_id, mapsheet_id, org_id):
    return f"""
    DECLARE @CUSTID INT = {org_id} 
    DECLARE @SID INT = {survey_id}
    DECLARE @MPSID INT = {mapsheet_id}

    SELECT t.Label FROM ( 
	    select DISTINCT DFF.Label
        from SbuFormDetails SFD
        INNER JOIN SbuFormFieldValue SFV ON SFV.SbuFormDetailId = SFD.Id
        INNER JOIN DataFormFields DFF ON DFF.Id = SFV.FieldId
        LEFT JOIN CustomerOrganisation O ON O.Id = DFF.CustomerOrganisationId
        where SFD.RefId = @SID AND  DFF.FormType IN (1, 2, 6) AND 
            SFD.SbuSurveyMapSheetId = @MPSID AND DFF.FieldType = 1
            AND DFF.CustomerOrganisationId = @CUSTID
    ) as t
    """

def CGI_new():
    return f"""
    --Task 22296 - Create a Lookup table and remove the enumeration class from the library to make the design  
    --flexible for future
    --
    --list these form types as a Look Up Table. The current supported form types are:
    CREATE TABLE [dbo].[LUTFormTypes](
        [Id] [smallint] NOT NULL PRIMARY KEY,
        [FormType] [char](64) NULL
    )
    GO

    --Task 22297 - Create a look up table for the form status and eliminate the FormStatus enumeration from HeathDataRepository
    ----  create a look up table to make the design flexible. The current form status supported are.
    CREATE TABLE [dbo].[LUTStatuses](
        [Id] [smallint] NOT NULL PRIMARY KEY,
        [Status] [char](64) NULL,
        [BusinessEntity] [smallint] NULL
    )
    GO

    --LUTBusinessEntities

    CREATE TABLE [dbo].[LUTBusinessEntities](
        [Id] [smallint] NOT NULL PRIMARY KEY,
        [EntityName] [char](64) NULL,
        [AlternativeName] [varchar] (128) NULL
    )
    GO
    -- Business Entity Type and status

    --Task 22298 - Create the master table for CGI form type (CGIMaster_SurveyID)
    ----construct the Master Record for CGI using the following columns. The columns marked with * are existing in the current SbuFormDetails table

    CREATE PROC [dbo].[SP_CreateDynamicTableForCGIMaster]    
    (    
    @SurveyId INT    
    )    
    AS    
    BEGIN    
    DECLARE @CGIMasterTable NVARCHAR(MAX)    
    SET @CGIMasterTable = 'IF (NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = ''dbo''     
                    AND  TABLE_NAME = ''CGIMaster_'+CAST(@SurveyId AS VARCHAR(10))+'''))    
    BEGIN    
    CREATE TABLE [dbo].[CGIMaster_'+CAST(@SurveyId AS VARCHAR(10))+'](  
    [UniqueId] UniqueIdentifier NOT NULL PRIMARY KEY,
    [Latitude] [float] NULL,  
    [Longitude] [float] NULL,  
    [Address1] [char] (128) NULL, 
    [Address2] [char] (128) NULL, 
    [City] [char] (128) NULL, 
    [MeterNumber] [char] (50) NULL, 
    [Legend] [char] (256) NULL,
    [Status] [Id] [int] NOT NULL,
    [IsReworkData] [bit] NOT NULL DEFAULT (0), 
    [IsAuditData] [bit] NOT NULL DEFAULT (0),
    )  ON [PRIMARY]   
    END  
    '    
    EXEC(@CGIMasterTable)    
    END

    --Task 22299 - Create slave/history table for the Forms submitted (CGIDetails_SurveyId)
    ----create the slave table with the following columns:

    CREATE PROC [dbo].[SP_CreateDynamicTableForCGIDetails]
    (    
    @SurveyId INT    
    )    
    AS    
    BEGIN    
    DECLARE @CGIDetailsTable NVARCHAR(MAX)    
    SET @CGIDetailsTable = 'IF (NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = ''dbo''     
                    AND  TABLE_NAME = ''CGIDetails_'+CAST(@SurveyId AS VARCHAR(10))+'''))    
    BEGIN    
    CREATE TABLE [dbo].[CGIDetails_'+CAST(@SurveyId AS VARCHAR(10))+'](  
    [UniqueId] UniqueIdentifier IDENTITY(1,1) NOT NULL PRIMARY KEY,
    [MasterRecordId] UniqueIdentifier NOT NULL,
    [Reason] [varchar](512) NULL, 
    [Comment] [varchar](512) NULL,
    [IsTagged] [bit] NOT NULL DEFAULT (0),  
    [Image] VARBINARY(MAX),
    [ContainerName] [Char] (64) NULL,
    [PDFFileName] [Char] (64) NULL,
    [PDFGenerationState] tinyint NULL,
    [CreatedBy] UniqueIdentifier NOT NULL, 
    [CreatedByName] [char](128) NULL, 
    [UpdatedBy] UniqueIdentifier NULL, 
    [UpdatedByName] [char](128) NULL, 
    [CreatedDate] [Datetime2] NULL, 
    [WhenCreated] [Date] NULL, 
    [UpdatedDate] [Datetime2] NULL, 
    [WhenUpdated] [Date] NULL,  
    )  ON [PRIMARY]   
    END  
    '    
    EXEC(@CGIDetailsTable)    
    END
    """

def ccccc():
    sql = f"""
    DECLARE @RowsToProcess  int
    DECLARE @CurrentRow     int
    DECLARE @SelectUniqueId     uniqueidentifier

    DECLARE @CGIRecordsTable TABLE (RowID int not null primary key identity(1,1), UniqueId uniqueidentifier)  
    INSERT into @CGIRecordsTable (UniqueId) SELECT UniqueId FROM [dbo].[SbuFormDetails] Where LinkedId IS NULL AND FormType = 5 AND RefId = @SurveyId; 

    SET @RowsToProcess=@@ROWCOUNT

    SET @CurrentRow=0
    WHILE @CurrentRow<@RowsToProcess
    BEGIN
        SET @CurrentRow=@CurrentRow+1
        SELECT 
            @SelectUniqueId=UniqueId
        FROM @CGIRecordsTable
        WHERE RowID=@CurrentRow
	
	    DECLARE  @SQL1 NVARCHAR(MAX) 
	    SET @SQL1 = N'                          
                            
	    IF (NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = ''dbo''                           
						AND TABLE_NAME = ''CGIMaster_'+CAST(@SurveyId AS VARCHAR(10))+'''))                                                  	
		    CREATE TABLE [dbo].[CGIMaster_' + CAST(@SurveyId AS VARCHAR(10)) + '](                          
		    [Id] UniqueIdentifier PRIMARY KEY NONCLUSTERED NOT NULL DEFAULT (newid()),  
		    [Latitude] [float] NULL,  
		    [Longitude] [float] NULL,  
		    [Address1] [char] (128) NULL, 
		    [Address2] [char] (128) NULL, 
		    [City] [char] (128) NULL, 
		    [MeterNumber] [char] (50) NULL, 
		    [Legend] [char] (256) NULL,
		    [Status] [int] NOT NULL,
		    [IsReworkData] [bit] NOT NULL DEFAULT (0), 
		    [IsAuditData] [bit] NOT NULL DEFAULT (0),
		    [CreatedDate] [Datetime2] NULL, 
		    [CreatedBy]  [varchar](256) NULL, 
	    )                      
                          
	    INSERT INTO CGIMaster_' + CAST(@SurveyId AS VARCHAR(10)) + '(	
			[Latitude]
			,[Longitude]
			,[Address1]
			,[Address2]
			,[City]
			,[MeterNumber]
			,[Legend]
			,[Status]
			,[IsReworkData]
			,[IsAuditData]
			,[CreatedDate]  
			,[CreatedBy] )                          
		SELECT 
			[Latitude]
			,[Longitude]
			,''''
			,''''
			,''''
			,''''
			,''''
			,[Status]
			,[IsReworkData]
			,[IsAuditData]
			,[CreatedDate]  
			,[CreatedBy] 
		FROM [dbo].[SbuFormDetails] 
		where LinkedId IS NULL AND FormType = 5 AND RefId = '+CAST(@SurveyId AS VARCHAR(10))+'';

	    DECLARE  @SQL2 NVARCHAR(MAX) 
	    SET @SQL2 = N'  
	    IF (NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = ''dbo''                           
						AND TABLE_NAME = ''CGIDetails_'+CAST(@SurveyId AS VARCHAR(10))+'''))                            
		CREATE TABLE [dbo].[CGIDetails_'+CAST(@SurveyId AS VARCHAR(10))+']( 
		    [Id] [uniqueidentifier] PRIMARY KEY NONCLUSTERED NOT NULL DEFAULT (newid()),
		    [MasterRecordId] UniqueIdentifier NOT NULL FOREIGN KEY REFERENCES [dbo].[CGIMaster_'+CAST(@SurveyId AS VARCHAR(10))+'] ([Id]),
		    [Reason] [varchar](512) NULL, 
		    [Comment] [varchar](512) NULL,
		    [IsTagged] [bit] NOT NULL DEFAULT (0),  
		    [Image] VARBINARY(MAX),
		    [ContainerName] [Char] (64) NULL,
		    [PDFFileName] [Char] (64) NULL,
		    [PDFGenerationState] tinyint NULL,
		    [CreatedDate] [Datetime2] NULL, 
		    [CreatedBy]  [varchar](256) NULL, 
		    [UpdatedDate] [Datetime2] NULL, 
		    [UpdatedBy] [varchar](256) NULL, 
	    )

		INSERT INTO [dbo].[CGIDetails_'+CAST(@SurveyId AS VARCHAR(10))+']
		([Id]
		,[MasterRecordId]
		,[Reason]
		,[Comment]
		,[IsTagged]
		,[Image]
		,[ContainerName]
		,[PDFFileName]
		,[PDFGenerationState]
		,[CreatedDate]
		,[CreatedBy]
		,[UpdatedDate]
		,[UpdatedBy])

		SELECT
		newid(),
		(SELECT ID FROM [dbo].[CGIDetails_'+CAST(@SurveyId AS VARCHAR(10))+'] WHERE LinkedId = '+CAST(@SelectUniqueId AS NVARCHAR(256))+') AS [MasterRecordId]
		'''' Reason,
		'''' Comment,
		'''' IsTagged,
		CAST('''' AS varbinary(max)) AS [Image],
		ContainerName,
		PdfFileName, 
		PDFGenerationState
		,[CreatedDate]  
		,[CreatedBy]  
		,[UpdatedDate]  
		,[UpdatedBy] 
		FROM [dbo].[SbuFormDetails] 
		where LinkedId = '+CAST(@SelectUniqueId AS NVARCHAR(256))+'';
    EXEC sp_executesql @SQL1;	
EXEC sp_executesql @SQL2;
END
    """