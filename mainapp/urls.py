from django.urls import path
from .views import *
urlpatterns = [
    path("",login, name="login"),
    path("dashboard/",dashboard, name="dashboard"),
    path('setup', setup, name='setup'),
	path("clientprofile/", clientprofile, name="clientprofile"),
	path("clientprofile_list/", clientprofile_list, name="clientprofile_list"),
	path("clientprofile_edit/<pk>/", clientprofile_edit, name="clientprofile_edit"),
	path("clientprofile_delete/<pk>/", clientprofile_delete, name="clientprofile_delete"),
    
	path("documentgroup/", documentgroup, name="documentgroup"),
	path("documentgroup_list/", documentgroup_list, name="documentgroup_list"),
	path("documentgroup_edit/<pk>/", documentgroup_edit, name="documentgroup_edit"),
	path("documentgroup_delete/<pk>/", documentgroup_delete, name="documentgroup_delete"),
    
	path("customdocumententity/", customdocumententity, name="customdocumententity"),
	path("customdocumententity_list/", customdocumententity_list, name="customdocumententity_list"),
	path("customdocumententity_edit/<pk>/", customdocumententity_edit, name="customdocumententity_edit"),
	path("customdocumententity_delete/<pk>/", customdocumententity_delete, name="customdocumententity_delete"),
    
	path("tasktemplate/", tasktemplate, name="tasktemplate"),
	path("tasktemplate_list/", tasktemplate_list, name="tasktemplate_list"),
	path("tasktemplate_edit/<pk>/", tasktemplate_edit, name="tasktemplate_edit"),
	path("tasktemplate_delete/<pk>/", tasktemplate_delete, name="tasktemplate_delete"),
    
	path("triogroup/", triogroup, name="triogroup"),
	path("triogroup_list/", triogroup_list, name="triogroup_list"),
	path("triogroup_edit/<pk>/", triogroup_edit, name="triogroup_edit"),
	path("triogroup_delete/<pk>/", triogroup_delete, name="triogroup_delete"),
    
	path("loancase/", loancase, name="loancase"),
    path("loancase_list/", loancase_list, name="loancase_list"),
	path("loancase_edit/<pk>/", loancase_edit, name="loancase_edit"),
	path("loancase_delete/<pk>/", loancase_delete, name="loancase_delete"),
    
	path("projects/", projects, name="projects"),
    path("projects_list/", projects_list, name="projects_list"),
	path("projects_edit/<pk>/", projects_edit, name="projects_edit"),
	path("projects_delete/<pk>/", projects_delete, name="projects_delete"),
    
	path("documenttype/", documenttype, name="documenttype"),
	path("documenttype_list/", documenttype_list, name="documenttype_list"),
	path("documenttype_edit/<pk>/", documenttype_edit, name="documenttype_edit"),
	path("documenttype_delete/<pk>/", documenttype_delete, name="documenttype_delete"),
    
	path("foldermaster/", foldermaster, name="foldermaster"),
	path("foldermaster_list/", foldermaster_list, name="foldermaster_list"),
	path("foldermaster_edit/<pk>/", foldermaster_edit, name="foldermaster_edit"),
	path("foldermaster_delete/<pk>/", foldermaster_delete, name="foldermaster_delete"),
	
	path("trioassignment/", trioassignment, name="trioassignment"),
	path("trioassignment_list/", trioassignment_list, name="trioassignment_list"),
	path("trioassignment_edit/<pk>/", trioassignment_edit, name="trioassignment_edit"),
	path("trioassignment_delete/<pk>/", trioassignment_delete, name="trioassignment_delete"),
    
	path("auditlog/", auditlog, name="auditlog"),
	path("auditlog_list/", auditlog_list, name="auditlog_list"),
	path("auditlog_edit/<pk>/", auditlog_edit, name="auditlog_edit"),
	path("auditlog_delete/<pk>/", auditlog_delete, name="auditlog_delete"),
    
	path("compliancechecklist/", compliancechecklist, name="compliancechecklist"),
	path("compliancechecklist_list/", compliancechecklist_list, name="compliancechecklist_list"),
	path("compliancechecklist_edit/<pk>/", compliancechecklist_edit, name="compliancechecklist_edit"),
	path("compliancechecklist_delete/<pk>/", compliancechecklist_delete, name="compliancechecklist_delete"),
    
	path("document/", document, name="document"),
	path("document_list/", document_list, name="document_list"),
	path("document_edit/<pk>/", document_edit, name="document_edit"),
	path("document_delete/<pk>/", document_delete, name="document_delete"),
    
	path("riskassessment/", riskassessment, name="riskassessment"),
	path("riskassessment_list/", riskassessment_list, name="riskassessment_list"),
	path("riskassessment_edit/<pk>/", riskassessment_edit, name="riskassessment_edit"),
	path("riskassessment_delete/<pk>/", riskassessment_delete, name="riskassessment_delete"),
    
	path("clientquery/", clientquery, name="clientquery"),
	path("clientquery_list/", clientquery_list, name="clientquery_list"),
	path("clientquery_edit/<pk>/", clientquery_edit, name="clientquery_edit"),
	path("clientquery_delete/<pk>/", clientquery_delete, name="clientquery_delete"),
    
	path("timesheet/", timesheet, name="timesheet"),
	path("timesheet_list/", timesheet_list, name="timesheet_list"),
	path("timesheet_edit/<pk>/", timesheet_edit, name="timesheet_edit"),
	path("timesheet_delete/<pk>/", timesheet_delete, name="timesheet_delete"),
    
	path("documentupload/", documentupload, name="documentupload"),
	path("documentupload_list/", documentupload_list, name="documentupload_list"),
	path("documentupload_edit/<pk>/", documentupload_edit, name="documentupload_edit"),
	path("documentupload_delete/<pk>/", documentupload_delete, name="documentupload_delete"),
    
	path("documentuploadaudit1/", documentuploadaudit1, name="documentuploadaudit1"),
	path("documentuploadaudit1_list/", documentuploadaudit1_list, name="documentuploadaudit1_list"),
	path("documentuploadaudit1_edit/<pk>/", documentuploadaudit1_edit, name="documentuploadaudit1_edit"),
	path("documentuploadaudit1_delete/<pk>/", documentuploadaudit1_delete, name="documentuploadaudit1_delete"),
    
	path("documentuploadhistory1/", documentuploadhistory1, name="documentuploadhistory1"),
	path("documentuploadhistory1_list/", documentuploadhistory1_list, name="documentuploadhistory1_list"),
	path("documentuploadhistory1_edit/<pk>/", documentuploadhistory1_edit, name="documentuploadhistory1_edit"),
	path("documentuploadhistory1_delete/<pk>/", documentuploadhistory1_delete, name="documentuploadhistory1_delete"),
    
	path("userprofile/", userprofile, name="userprofile"),
	path("userprofile_list/", userprofile_list, name="userprofile_list"),
	path("userprofile_edit/<pk>/", userprofile_edit, name="userprofile_edit"),
	path("userprofile_delete/<pk>/", userprofile_delete, name="userprofile_delete"),
    
	path("documentaccess/", documentaccess, name="documentaccess"),
	path("documentaccess_list/", documentaccess_list, name="documentaccess_list"),
	path("documentaccess_edit/<pk>/", documentaccess_edit, name="documentaccess_edit"),
	path("documentaccess_delete/<pk>/", documentaccess_delete, name="documentaccess_delete"),
    
	path("filedownloadreason/", filedownloadreason, name="filedownloadreason"),
	path("filedownloadreason_list/", filedownloadreason_list, name="filedownloadreason_list"),
	path("filedownloadreason_edit/<pk>/", filedownloadreason_edit, name="filedownloadreason_edit"),
	path("filedownloadreason_delete/<pk>/", filedownloadreason_delete, name="filedownloadreason_delete"),
    
	path("caseassignment/", caseassignment, name="caseassignment"),
	path("caseassignment_list/", caseassignment_list, name="caseassignment_list"),
	path("caseassignment_edit/<pk>/", caseassignment_edit, name="caseassignment_edit"),
	path("caseassignment_delete/<pk>/", caseassignment_delete, name="caseassignment_delete"),
    
	path("triogroupmember/", triogroupmember, name="triogroupmember"),
	path("triogroupmember_list/", triogroupmember_list, name="triogroupmember_list"),
	path("triogroupmember_edit/<pk>/", triogroupmember_edit, name="triogroupmember_edit"),
	path("triogroupmember_delete/<pk>/", triogroupmember_delete, name="triogroupmember_delete"),
    
	path("trioprofile/", trioprofile, name="trioprofile"),
	path("trioprofile_list/", trioprofile_list, name="trioprofile_list"),
	path("trioprofile_edit/<pk>/", trioprofile_edit, name="trioprofile_edit"),
	path("trioprofile_delete/<pk>/", trioprofile_delete, name="trioprofile_delete"),
    
	path("finalreport/", finalreport, name="finalreport"),
	path("finalreport_list/", finalreport_list, name="finalreport_list"),
	path("finalreport_edit/<pk>/", finalreport_edit, name="finalreport_edit"),
	path("finalreport_delete/<pk>/", finalreport_delete, name="finalreport_delete"),
    
	path("task/", task, name="task"),
	path("task_list/", task_list, name="task_list"),
	path("task_edit/<pk>/", task_edit, name="task_edit"),
	path("task_delete/<pk>/", task_delete, name="task_delete"),
    
	path("taskauditlog/", taskauditlog, name="taskauditlog"),
	path("taskauditlog_list/", taskauditlog_list, name="taskauditlog_list"),
	path("taskauditlog_edit/<pk>/", taskauditlog_edit, name="taskauditlog_edit"),
	path("taskauditlog_delete/<pk>/", taskauditlog_delete, name="taskauditlog_delete"),
    
	path("taskdeliverable/", taskdeliverable, name="taskdeliverable"),
	path("taskdeliverable_list/", taskdeliverable_list, name="taskdeliverable_list"),
	path("taskdeliverable_edit/<pk>/", taskdeliverable_edit, name="taskdeliverable_edit"),
	path("taskdeliverable_delete/<pk>/", taskdeliverable_delete, name="taskdeliverable_delete"),
    
	path("tasktimesheet/", tasktimesheet, name="tasktimesheet"),
	path("tasktimesheet_list/", tasktimesheet_list, name="tasktimesheet_list"),
	path("tasktimesheet_edit/<pk>/", tasktimesheet_edit, name="tasktimesheet_edit"),
	path("tasktimesheet_delete/<pk>/", tasktimesheet_delete, name="tasktimesheet_delete"),
	path("taskhours/<int:pk>/", taskhours, name="taskhours"),
    
	path("timesheetentry/", timesheetentry, name="timesheetentry"),
	path("timesheetentry_list/", timesheetentry_list, name="timesheetentry_list"),
	path("timesheetentry_edit/<pk>/", timesheetentry_edit, name="timesheetentry_edit"),
	path("timesheetentry_delete/<pk>/", timesheetentry_delete, name="timesheetentry_delete"),
    
	path("timesheetattachment/", timesheetattachment, name="timesheetattachment"),
	path("timesheetattachment_list/", timesheetattachment_list, name="timesheetattachment_list"),
	path("timesheetattachment_edit/<pk>/", timesheetattachment_edit, name="timesheetattachment_edit"),
	path("timesheetattachment_delete/<pk>/", timesheetattachment_delete, name="timesheetattachment_delete"),
    
	path("timesheetdocument/", timesheetdocument, name="timesheetdocument"),
	path("timesheetdocument_list/", timesheetdocument_list, name="timesheetdocument_list"),
	path("timesheetdocument_edit/<pk>/", timesheetdocument_edit, name="timesheetdocument_edit"),
	path("timesheetdocument_delete/<pk>/", timesheetdocument_delete, name="timesheetdocument_delete"),
    
	path("workschedule/", workschedule, name="workschedule"),
	path("workschedule_list/", workschedule_list, name="workschedule_list"),
	path("workschedule_edit/<pk>/", workschedule_edit, name="workschedule_edit"),
	path("workschedule_delete/<pk>/", workschedule_delete, name="workschedule_delete"),
    
	path("taskextrahoursrequest/", taskextrahoursrequest, name="taskextrahoursrequest"),
	path("taskextrahoursrequest_edit/<pk>/", taskextrahoursrequest_edit, name="taskextrahoursrequest_edit"),
	path("taskextrahoursrequest_delete/<pk>/", taskextrahoursrequest_delete, name="taskextrahoursrequest_delete"),
    
	path("meetings/", meetings, name="meetings"),
	path("meetings_edit/<pk>/", meetings_edit, name="meetings_edit"),
	path("meetings_delete/<pk>/", meetings_delete, name="meetings_delete"),
    
	path("auditorprofile/", auditorprofile, name="auditorprofile"),
	path("auditorprofile_list/", auditorprofile_list, name="auditorprofile_list"),
	path("auditorprofile_edit/<pk>/", auditorprofile_edit, name="auditorprofile_edit"),
	path("auditorprofile_delete/<pk>/", auditorprofile_delete, name="auditorprofile_delete"),
    
	path("marketingagentprofile/", marketingagentprofile, name="marketingagentprofile"),
	path("marketingagentprofile_list/", marketingagentprofile_list, name="marketingagentprofile_list"),
	path("marketingagentprofile_edit/<pk>/", marketingagentprofile_edit, name="marketingagentprofile_edit"),
	path("marketingagentprofile_delete/<pk>/", marketingagentprofile_delete, name="marketingagentprofile_delete"),
    
	path("issuereport/", issuereport, name="issuereport"),
	path("issuereport_list/", issuereport_list, name="issuereport_list"),
	path("issuereport_edit/<pk>/", issuereport_edit, name="issuereport_edit"),
	path("issuereport_delete/<pk>/", issuereport_delete, name="issuereport_delete"),
    
	path("notification/", notification, name="notification"),
	path("notification_list/", notification_list, name="notification_list"),
	path("notification_edit/<pk>/", notification_edit, name="notification_edit"),
	path("notification_delete/<pk>/", notification_delete, name="notification_delete"),
    
	path("lawyerprofile/", lawyerprofile, name="lawyerprofile"),
	path("lawyerprofile_list/", lawyerprofile_list, name="lawyerprofile_list"),
	path("lawyerprofile_edit/<pk>/", lawyerprofile_edit, name="lawyerprofile_edit"),
	path("lawyerprofile_delete/<pk>/", lawyerprofile_delete, name="lawyerprofile_delete"),
    
	path("members/", members, name="members"),
	path("members_list/", members_list, name="members_list"),
	path("members_edit/<pk>/", members_edit, name="members_edit"),
	path("members_delete/<pk>/", members_delete, name="members_delete"),
    
	path("events/", events, name="events"),
	path("events_list/", events_list, name="events_list"),
	path("events_edit/<pk>/", events_edit, name="events_edit"),
	path("events_delete/<pk>/", events_delete, name="events_delete"),
    
	path("stafffeedback/", stafffeedback, name="stafffeedback"),
	path("stafffeedback_edit/<pk>/", stafffeedback_edit, name="stafffeedback_edit"),
	path("stafffeedback_delete/<pk>/", stafffeedback_delete, name="stafffeedback_delete"),
    
	path("taskassignment/", taskassignment, name="taskassignment"),
	path("taskassignment_list/", taskassignment_list, name="taskassignment_list"),
	path("taskassignment_edit/<pk>/", taskassignment_edit, name="taskassignment_edit"),
	path("taskassignment_delete/<pk>/", taskassignment_delete, name="taskassignment_delete"),
    


	path("select_company/", select_company, name="select_company"),
	path("select_branch/<int:pk>/", select_branch, name="select_branch"),
	path("document_entity/", document_entity, name="document_entity"),
	path("get_documents/<str:entityId>/", get_documents, name="get_documents"),


]