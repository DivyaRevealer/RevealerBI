import { useState } from 'react';
import { t, styled } from '@superset-ui/core';
import { Input, TextArea } from 'src/components/Input';
import { CronPicker } from 'src/components/CronPicker';
import Button from 'src/components/Button';

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

export default function SchedulerView() {
  const [dashboardId, setDashboardId] = useState('');
  const [sqlQuery, setSqlQuery] = useState('');
  const [databaseId, setDatabaseId] = useState('');
  const [schema, setSchema] = useState('');
  const [schedule, setSchedule] = useState('0 0 * * *');

  const handleSubmit = () => {
    // placeholder submit handler
    // eslint-disable-next-line no-console
    console.log({ dashboardId, sqlQuery, databaseId, schema, schedule });
  };

  return (
    <Container>
      <h2>{t('Scheduler')}</h2>
      <Field>
        <div className="control-label">{t('Dashboard ID')}</div>
        <Input value={dashboardId} onChange={e => setDashboardId(e.target.value)} />
      </Field>
      <Field>
        <div className="control-label">{t('SQL Query')}</div>
        <TextArea
          rows={4}
          value={sqlQuery}
          onChange={e => setSqlQuery(e.target.value)}
        />
      </Field>
      <Field>
        <div className="control-label">{t('Database ID')}</div>
        <Input value={databaseId} onChange={e => setDatabaseId(e.target.value)} />
      </Field>
      <Field>
        <div className="control-label">{t('Schema')}</div>
        <Input value={schema} onChange={e => setSchema(e.target.value)} />
      </Field>
      <Field>
        <div className="control-label">{t('Schedule time')}</div>
        <CronPicker clearButton={false} value={schedule} setValue={setSchedule} />
      </Field>
      <Button buttonStyle="primary" onClick={handleSubmit}>
        {t('Save')}
      </Button>
    </Container>
  );
}
