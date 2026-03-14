import { useCallback, useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { deleteTask, getStats, getTasks } from '../api/api';
import TaskModal from '../components/TaskModal';
import { useAuth } from '../context/AuthContext';

const statusMeta = {
  TODO:        { label: 'To Do',       cls: 'badge-todo' },
  IN_PROGRESS: { label: 'In Progress', cls: 'badge-inprogress' },
  DONE:        { label: 'Done',        cls: 'badge-done' },
};
const priorityMeta = {
  LOW:    { cls: 'badge-low' },
  MEDIUM: { cls: 'badge-medium' },
  HIGH:   { cls: 'badge-high' },
};

const Dashboard = () => {
  const { user } = useAuth();
  const [tasks, setTasks]       = useState([]);
  const [stats, setStats]       = useState(null);
  const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0 });
  const [filters, setFilters]   = useState({ status: '', priority: '', search: '' });
  const [page, setPage]         = useState(1);
  const [loading, setLoading]   = useState(false);
  const [modalTask, setModalTask] = useState(undefined); // undefined = closed, null = create, obj = edit

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, limit: 8 };
      if (filters.status)   params.status   = filters.status;
      if (filters.priority) params.priority = filters.priority;
      if (filters.search)   params.search   = filters.search;
      const { data } = await getTasks(params);
      setTasks(data.data.tasks);
      setPagination(data.data.pagination);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }, [page, filters]);

  const fetchStats = useCallback(async () => {
    try {
      const { data } = await getStats();
      setStats(data.data.stats);
    } catch (_) {}
  }, []);

  useEffect(() => { fetchTasks(); fetchStats(); }, [fetchTasks, fetchStats]);

  const handleDelete = async (id) => {
    if (!confirm('Delete this task?')) return;
    try {
      await deleteTask(id);
      toast.success('Task deleted');
      fetchTasks(); fetchStats();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Delete failed');
    }
  };

  const handleFilterChange = (e) => {
    setFilters((f) => ({ ...f, [e.target.name]: e.target.value }));
    setPage(1);
  };

  return (
    <div className="page-wrap">
      {/* Stats */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card"><div className="stat-num">{stats.total}</div><div className="stat-label">Total</div></div>
          <div className="stat-card todo"><div className="stat-num">{stats.byStatus.TODO || 0}</div><div className="stat-label">To Do</div></div>
          <div className="stat-card inprogress"><div className="stat-num">{stats.byStatus.IN_PROGRESS || 0}</div><div className="stat-label">In Progress</div></div>
          <div className="stat-card done"><div className="stat-num">{stats.byStatus.DONE || 0}</div><div className="stat-label">Done</div></div>
        </div>
      )}

      {/* Toolbar */}
      <div className="toolbar">
        <h2 className="section-title">
          {user?.role === 'ADMIN' ? 'All Tasks' : 'My Tasks'}
        </h2>
        <div className="toolbar-right">
          <input
            name="search" placeholder="Search…" value={filters.search}
            onChange={handleFilterChange} className="search-input"
          />
          <select name="status" value={filters.status} onChange={handleFilterChange}>
            <option value="">All Statuses</option>
            <option value="TODO">To Do</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="DONE">Done</option>
          </select>
          <select name="priority" value={filters.priority} onChange={handleFilterChange}>
            <option value="">All Priorities</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
          </select>
          <button className="btn btn-primary" onClick={() => setModalTask(null)}>+ New Task</button>
        </div>
      </div>

      {/* Table */}
      <div className="table-wrap">
        {loading ? (
          <div className="table-loading"><div className="spinner dark" /></div>
        ) : tasks.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <p>No tasks found. Create your first one!</p>
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Task</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Due Date</th>
                {user?.role === 'ADMIN' && <th>Owner</th>}
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((t) => (
                <tr key={t.id}>
                  <td>
                    <div className="task-title">{t.title}</div>
                    {t.description && <div className="task-desc">{t.description}</div>}
                  </td>
                  <td>
                    <span className={`badge ${statusMeta[t.status]?.cls}`}>
                      {statusMeta[t.status]?.label}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${priorityMeta[t.priority]?.cls}`}>{t.priority}</span>
                  </td>
                  <td className="muted-cell">
                    {t.dueDate ? new Date(t.dueDate).toLocaleDateString() : '—'}
                  </td>
                  {user?.role === 'ADMIN' && (
                    <td className="muted-cell">{t.user?.name}</td>
                  )}
                  <td>
                    <div className="action-btns">
                      <button className="btn btn-sm btn-outline" onClick={() => setModalTask(t)}>Edit</button>
                      <button className="btn btn-sm btn-danger" onClick={() => handleDelete(t.id)}>Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {/* Pagination */}
        {!loading && pagination.pages > 1 && (
          <div className="pagination">
            <button className="btn btn-sm btn-outline" disabled={page <= 1} onClick={() => setPage(page - 1)}>← Prev</button>
            <span className="page-info">Page {pagination.page} of {pagination.pages}</span>
            <button className="btn btn-sm btn-outline" disabled={page >= pagination.pages} onClick={() => setPage(page + 1)}>Next →</button>
          </div>
        )}
      </div>

      {/* Task Modal */}
      {modalTask !== undefined && (
        <TaskModal
          task={modalTask}
          onClose={() => setModalTask(undefined)}
          onSaved={() => { fetchTasks(); fetchStats(); }}
        />
      )}
    </div>
  );
};

export default Dashboard;
