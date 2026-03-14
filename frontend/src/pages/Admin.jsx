import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { deleteUser, getUsers, updateRole } from '../api/api';
import { useAuth } from '../context/AuthContext';

const Admin = () => {
  const { user: currentUser } = useAuth();
  const [users, setUsers]     = useState([]);
  const [pagination, setPagination] = useState({ page: 1, pages: 1 });
  const [page, setPage]       = useState(1);
  const [loading, setLoading] = useState(false);

  const fetchUsers = async (p = page) => {
    setLoading(true);
    try {
      const { data } = await getUsers({ page: p, limit: 10 });
      setUsers(data.data.users);
      setPagination(data.data.pagination);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchUsers(); }, [page]);

  const handleRoleChange = async (id, role) => {
    try {
      await updateRole(id, { role });
      toast.success('Role updated');
      fetchUsers();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to update role');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this user and all their tasks?')) return;
    try {
      await deleteUser(id);
      toast.success('User deleted');
      fetchUsers();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Delete failed');
    }
  };

  return (
    <div className="page-wrap">
      <h2 className="section-title" style={{ marginBottom: 20 }}>User Management</h2>

      <div className="table-wrap">
        {loading ? (
          <div className="table-loading"><div className="spinner dark" /></div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Joined</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>{u.name}</td>
                  <td className="muted-cell">{u.email}</td>
                  <td>
                    <select
                      value={u.role}
                      onChange={(e) => handleRoleChange(u.id, e.target.value)}
                      className="role-select"
                      disabled={u.id === currentUser.id}
                    >
                      <option value="USER">USER</option>
                      <option value="ADMIN">ADMIN</option>
                    </select>
                  </td>
                  <td className="muted-cell">{new Date(u.createdAt).toLocaleDateString()}</td>
                  <td>
                    {u.id !== currentUser.id ? (
                      <button className="btn btn-sm btn-danger" onClick={() => handleDelete(u.id)}>
                        Delete
                      </button>
                    ) : (
                      <span className="muted" style={{ fontSize: '.8rem' }}>You</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {!loading && pagination.pages > 1 && (
          <div className="pagination">
            <button className="btn btn-sm btn-outline" disabled={page <= 1} onClick={() => setPage(page - 1)}>← Prev</button>
            <span className="page-info">Page {pagination.page} of {pagination.pages}</span>
            <button className="btn btn-sm btn-outline" disabled={page >= pagination.pages} onClick={() => setPage(page + 1)}>Next →</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Admin;
