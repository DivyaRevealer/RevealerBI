import { useState } from 'react';
//import { t, styled } from '@superset-ui/core';
import { t, styled, SupersetClient } from '@superset-ui/core';
import { Input, TextArea } from 'src/components/Input';
import { CronPicker } from 'src/components/CronPicker';
import Button from 'src/components/Button';
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
  const [dashboardId, setDashboardId] = useState('');
  const [sqlQuery, setSqlQuery] = useState('');
  const [databaseId, setDatabaseId] = useState('');
  const [schema, setSchema] = useState('');
  const [schedule, setSchedule] = useState('0 0 * * *');

  const handleSubmit = async () => {
    try {
      await SupersetClient.post({
        endpoint: '/api/v1/scheduler/jobs',
        jsonPayload: {
          dashboard_id: dashboardId,
          sql: sqlQuery,
          database_id: databaseId,
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