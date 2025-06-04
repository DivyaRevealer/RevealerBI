import { useState } from 'react';
//import { t, styled } from '@superset-ui/core';
import { useMemo, useState } from 'react';
import { t, styled, SupersetClient } from '@superset-ui/core';
import { Input, TextArea } from 'src/components/Input';
import { CronPicker } from 'src/components/CronPicker';
import Button from 'src/components/Button';
import AsyncSelect from 'src/components/Select/AsyncSelect';
import rison from 'rison';
import { FilterOperator, SelectOption } from 'src/components/ListView';
import withToasts, { ToastProps } from 'src/components/MessageToasts/withToasts';

const Container = styled.div`
  margin: ${({ theme }) => theme.gridUnit * 4}px;
  max-width: ${({ theme }) => theme.gridUnit * 120}px;
`;

const Field = styled.div`
  margin-bottom: ${({ theme }) => theme.gridUnit * 4}px;

  .control-label {
    display: block;
    margin-bottom: ${({ theme }) => theme.gridUnit}px;
  }
`;

//export default function SchedulerView() {
function SchedulerView({ addSuccessToast, addDangerToast }: ToastProps) {
  //const [dashboardId, setDashboardId] = useState('');
  const [dashboard, setDashboard] = useState<SelectOption | null>(null);
  const [sqlQuery, setSqlQuery] = useState('');
  //const [databaseId, setDatabaseId] = useState('');
  const [database, setDatabase] = useState<SelectOption | null>(null);
  const [schema, setSchema] = useState('');
  const [schedule, setSchedule] = useState('0 0 * * *');
  
  
  const loadDashboards = useMemo(
    () =>
      async (
        input = '',
        page: number,
        pageSize: number,
      ): Promise<{ data: SelectOption[]; totalCount: number }> => {
        const filters = input
          ? {
              filters: [
                {
                  col: 'dashboard_title',
                  opr: FilterOperator.StartsWith,
                  value: input,
                },
              ],
            }
          : {};
        const query = rison.encode({
          columns: ['dashboard_title', 'id'],
          keys: ['none'],
          order_column: 'dashboard_title',
          order_direction: 'asc',
          page,
          page_size: pageSize,
          ...filters,
        });
        const { json } = await SupersetClient.get({
          endpoint: `/api/v1/dashboard/?q=${query}`,
        });
        const data = (json.result || []).map((row: any) => ({
          label: row.dashboard_title,
          value: row.id,
        }));
        return { data, totalCount: json.count ?? data.length };
      },
    [],
  );

  const loadDatabases = useMemo(
    () =>
      async (
        input = '',
        page: number,
        pageSize: number,
      ): Promise<{ data: SelectOption[]; totalCount: number }> => {
        const query = rison.encode({
          order_column: 'database_name',
          order_direction: 'asc',
          page,
          page_size: pageSize,
          filters: input
            ? [
                { col: 'database_name', opr: 'ct', value: input },
              ]
            : [],
        });
        const { json } = await SupersetClient.get({
          endpoint: `/api/v1/database/?q=${query}`,
        });
        const data = (json.result || []).map((row: any) => ({
          label: row.database_name,
          value: row.id,
        }));
        return { data, totalCount: json.count ?? data.length };
      },
    [],
  );

  const handleSubmit = async () => {
    try {
      await SupersetClient.post({
        endpoint: '/api/v1/scheduler/jobs',
        jsonPayload: {
          //dashboard_id: dashboardId,
		  dashboard_id: dashboard?.value,
          sql: sqlQuery,
          //database_id: databaseId,
		  database_id: database?.value,
          schema,
          schedule,
        },
      });
      addSuccessToast(t('Job saved'));
    } catch (error) {
      addDangerToast(t('Error saving job'));
    }
  };

  return (
    <Container>
      <h2>{t('Scheduler')}</h2>
      <Field>
		  <div className="control-label">{t('Dashboard ID')}</div>
		  <Input
			aria-label={t('Dashboard ID')}
			value={dashboardId}
			onChange={e => setDashboardId(e.target.value)}
		  />
		  
		  <div className="control-label">{t('Dashboard')}</div>
		  <AsyncSelect
			ariaLabel={t('Dashboard')}
			value={dashboard || undefined}
			onChange={option => setDashboard(option as SelectOption)}
			options={loadDashboards}
			data-test="dashboard-select"
		  />
		</Field>
      <Field>
        <div className="control-label">{t('SQL Query')}</div>
        <TextArea
		  aria-label={t('SQL Query')}
          rows={4}
          value={sqlQuery}
          onChange={e => setSqlQuery(e.target.value)}
        />
      </Field>
      <Field>
        <div className="control-label">{t('Database ID')}</div>
	    <Input
		  aria-label={t('Database ID')}
		  value={databaseId}
		  onChange={e => setDatabaseId(e.target.value)}
		/>
		 <div className="control-label">{t('Database')}</div>
        <AsyncSelect
          ariaLabel={t('Database')}
          value={database || undefined}
          onChange={option => setDatabase(option as SelectOption)}
          options={loadDatabases}
          data-test="database-select"
        />
      </Field>
      <Field>
        <div className="control-label">{t('Schema')}</div>
        <Input
          aria-label={t('Schema')}
          value={schema}
          onChange={e => setSchema(e.target.value)}
        />
      </Field>
      <Field>
        <div className="control-label">{t('Schedule time')}</div>
        <CronPicker
          aria-label={t('Schedule time')}
          clearButton={false}
          value={schedule}
          setValue={setSchedule}
        />
      </Field>
      <Button buttonStyle="primary" onClick={handleSubmit}>
        {t('Save')}
      </Button>
    </Container>
  );
}
}

export default withToasts(SchedulerView);