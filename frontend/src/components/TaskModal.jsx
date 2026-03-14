import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { createTask, updateTask } from '../api/api';

const EMPTY = { title: '', description: '', status: 'TODO', priority: 'MEDIUM', dueDate: '' };

const TaskModal = ({ task, onClose, onSaved }) => {
  const [form, setForm]     = useState(EMPTY);
  const [loading, setLoading] = useState(false);
  const editing = !!task;

  useEffect(() => {
    if (task) {
      setForm({
        title:       task.title,
        description: task.description || '',
        status:      task.status,
        priority:    task.priority,
        dueDate:     task.dueDate ? task.dueDate.slice(0, 10) : '',
      });
    } else {
      setForm(EMPTY);
    }
  }, [task]);

  const handleChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        ...form,
        dueDate:     form.dueDate ? new Date(form.dueDate).toISOString() : undefined,
        description: form.description || undefined,
      };
      if (editing) {
        await updateTask(task.id, payload);
        toast.success('Task updated');
      } else {
        await createTask(payload);
        toast.success('Task created');
      }
      onSaved();
      onClose();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>{editing ? 'Edit Task' : 'New Task'}</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Title *</label>
            <input name="title" value={form.title} onChange={handleChange} required placeholder="Task title" />
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea name="description" value={form.description} onChange={handleChange} placeholder="Optional…" rows={3} />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Status</label>
              <select name="status" value={form.status} onChange={handleChange}>
                <option value="TODO">To Do</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="DONE">Done</option>
              </select>
            </div>
            <div className="form-group">
              <label>Priority</label>
              <select name="priority" value={form.priority} onChange={handleChange}>
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Due Date</label>
            <input name="dueDate" type="date" value={form.dueDate} onChange={handleChange} />
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-ghost" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? <span className="spinner" /> : editing ? 'Save Changes' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TaskModal;
