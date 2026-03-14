import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    toast.success('Logged out');
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <Link to="/dashboard" className="brand">⚡ TaskManager</Link>
      {user && (
        <div className="nav-links">
          <Link to="/dashboard">Tasks</Link>
          <Link to="/profile">Profile</Link>
          {user.role === 'ADMIN' && <Link to="/admin">Admin</Link>}
          <div className="nav-user">
            <span>{user.name}</span>
            <span className={`role-badge ${user.role === 'ADMIN' ? 'admin' : 'user'}`}>{user.role}</span>
          </div>
          <button className="btn btn-ghost" onClick={handleLogout}>Logout</button>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
