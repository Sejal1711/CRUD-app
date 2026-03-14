import { useState } from 'react';
import toast from 'react-hot-toast';
import { updateProfile } from '../api/api';
import { useAuth } from '../context/AuthContext';

const Profile = () => {
  const { user, setUser } = useAuth();
  const [form, setForm]     = useState({ name: user?.name || '', password: '' });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const body = {};
      if (form.name && form.name !== user.name) body.name = form.name;
      if (form.password) body.password = form.password;
      if (!Object.keys(body).length) { toast('Nothing to update', { icon: 'ℹ️' }); setLoading(false); return; }
      const { data } = await updateProfile(user.id, body);
      setUser(data.data.user);
      toast.success('Profile updated!');
      setForm((f) => ({ ...f, password: '' }));
    } catch (err) {
      const msg = err.response?.data?.errors
        ? err.response.data.errors.map((e) => e.message).join(', ')
        : err.response?.data?.message || 'Update failed';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-wrap" style={{ maxWidth: 520 }}>
      <h2 className="section-title" style={{ marginBottom: 24 }}>My Profile</h2>

      <div className="card" style={{ marginBottom: 20 }}>
        <div className="profile-row"><span className="profile-key">Name</span><span>{user?.name}</span></div>
        <div className="profile-row"><span className="profile-key">Email</span><span>{user?.email}</span></div>
        <div className="profile-row">
          <span className="profile-key">Role</span>
          <span className={`role-badge ${user?.role === 'ADMIN' ? 'admin' : 'user'}`}>{user?.role}</span>
        </div>
        <div className="profile-row">
          <span className="profile-key">Joined</span>
          <span>{user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : '—'}</span>
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: 18, fontSize: '1rem' }}>Update Profile</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Name</label>
            <input name="name" value={form.name} onChange={handleChange} placeholder="Your name" />
          </div>
          <div className="form-group">
            <label>New Password <span className="muted">(leave blank to keep)</span></label>
            <input name="password" type="password" value={form.password}
              onChange={handleChange} placeholder="NewPass@123" />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? <span className="spinner" /> : 'Save Changes'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Profile;
