from import_export import resources
from .models import Indicator, CollectedData, Country, WorkflowLevel1, Sector, DisaggregationValue, Frequency
from workflow.models import WorkflowLevel2, TolaUser
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export import fields


class IndicatorResource(resources.ModelResource):

    # country = fields.Field(column_name='country', attribute='country', widget=ManyToManyWidget(Program, field='country'))
    indicator_type = fields.Field(column_name='indicator types', attribute='indicator_types')
    objectives = fields.Field(column_name='objectives', attribute='objectives_list')
    strategic_objectives = fields.Field(column_name='strategic objectives', attribute='strategicobjectives_list')
    workflowlevel1 = fields.Field(column_name='workflowlevel1', attribute='workflowlevel1')
    sector = fields.Field(column_name='sector', attribute='sector', widget=ForeignKeyWidget(Sector, 'sector'))
    reporting_frequency = fields.Field(column_name='reporting_frequency', attribute='reporting_frequency', widget=ForeignKeyWidget(Frequency, 'frequency'))
    level = fields.Field(column_name='levels', attribute='levels')
    disaggregation = fields.Field(column_name='disaggregation', attribute='disaggregations')
    approval_submitted_by = fields.Field(column_name='approval submitted by', attribute='approval_submitted_by', widget=ForeignKeyWidget(TolaUser, 'name'))
    approved_by = fields.Field(column_name='approved by', attribute='approved_by', widget=ForeignKeyWidget(TolaUser, 'name'))

    class Meta:
        model = Indicator
        exclude = ('create_date','edit_date','owner','id','strategic_objective','objective')


class IndicatorAdmin(ImportExportModelAdmin):
    resource_class = IndicatorResource


class CollectedDataResource(resources.ModelResource):

    indicator = fields.Field(column_name='indicator', attribute='indicator',  widget=ForeignKeyWidget(Indicator, 'name_clean'))
    indicator_number = fields.Field(column_name='indicator_number', attribute='indicator', widget=ForeignKeyWidget(Indicator, 'number'))
    indicator_level = fields.Field(column_name='indicator_level', attribute='indicator',widget=ForeignKeyWidget(Indicator, 'levels'))
    agreement = fields.Field(column_name='agreement', attribute='agreement',  widget=ForeignKeyWidget(WorkflowLevel2, 'project_name_clean'))
    complete = fields.Field(column_name='complete', attribute='complete',  widget=ForeignKeyWidget(WorkflowLevel2, 'project_name_clean'))
    workflowlevel1 = fields.Field(column_name='workflowlevel1', attribute='workflowlevel1', widget=ForeignKeyWidget(WorkflowLevel1, 'name'))
    disaggregations = fields.Field(column_name='dissaggregations', attribute='disaggregations')

    class Meta:
        model = CollectedData
        exclude = ('create_date','edit_date')


class CollectedDataAdmin(ImportExportModelAdmin):
    resource_class = CollectedDataResource