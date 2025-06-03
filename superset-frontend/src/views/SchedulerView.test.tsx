import fetchMock from 'fetch-mock';
import { t } from '@superset-ui/core';
import { render, screen, waitFor, userEvent } from 'spec/helpers/testing-library';
import SchedulerView from 'src/views/SchedulerView';

const endpoint = '/api/v1/scheduler/jobs';

const mockedProps = {
  addSuccessToast: jest.fn(),
  addDangerToast: jest.fn(),
};

afterEach(() => {
  fetchMock.restore();
  jest.clearAllMocks();
});

test('saves a job and shows success toast', async () => {
  fetchMock.post(endpoint, {});
  render(<SchedulerView {...mockedProps} />, { useRedux: true });

  userEvent.type(screen.getByLabelText('Dashboard ID'), '10');
  userEvent.type(screen.getByLabelText('SQL Query'), 'select 1');
  userEvent.type(screen.getByLabelText('Database ID'), '1');
  userEvent.type(screen.getByLabelText('Schema'), 'public');

  userEvent.click(screen.getByText('Save'));

  await waitFor(() => {
    expect(fetchMock.calls(endpoint)).toHaveLength(1);
  });

  const [url, opts] = fetchMock.lastCall(endpoint) as [string, RequestInit];
  expect(JSON.parse(opts.body as string)).toEqual({
    dashboard_id: '10',
    sql: 'select 1',
    database_id: '1',
    schema: 'public',
    schedule: '0 0 * * *',
  });
  expect(mockedProps.addSuccessToast).toHaveBeenCalledWith(t('Job saved'));
});

