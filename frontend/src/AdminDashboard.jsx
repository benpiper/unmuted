import React, { useState, useEffect, useCallback } from 'react';
import {
  Box, Typography, Paper, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Button, IconButton,
  Chip, Stack, CircularProgress, Tooltip
} from '@mui/material';
import {
  CheckCircle as ApproveIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  AdminPanelSettings as PromoteIcon,
  PersonRemove as DemoteIcon
} from '@mui/icons-material';

export default function AdminDashboard({ apiFetch, apiBase }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      const res = await apiFetch(`${apiBase}/api/admin/users`);
      if (res.ok) {
        const data = await res.json();
        setUsers(data);
      }
    } catch (err) {
      console.error("Failed to fetch users", err);
    } finally {
      setLoading(false);
    }
  }, [apiFetch, apiBase]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleApprove = async (userId) => {
    try {
      const res = await apiFetch(`${apiBase}/api/admin/users/${userId}/approve`, {
        method: 'POST'
      });
      if (res.ok) {
        fetchUsers();
      }
    } catch (err) {
      console.error("Failed to approve user", err);
    }
  };

  const handleDelete = async (userId) => {
    if (!window.confirm("Are you sure you want to delete this user? This action cannot be undone.")) return;
    try {
      const res = await apiFetch(`${apiBase}/api/admin/users/${userId}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        fetchUsers();
      }
    } catch (err) {
      console.error("Failed to delete user", err);
    }
  };

  const handlePromoteAdmin = async (userId) => {
    if (!window.confirm("Promote this user to admin? They will have access to user management.")) return;
    try {
      const res = await apiFetch(`${apiBase}/api/admin/users/${userId}/promote-admin`, {
        method: 'POST'
      });
      if (res.ok) {
        fetchUsers();
      }
    } catch (err) {
      console.error("Failed to promote user", err);
    }
  };

  const handleDemoteAdmin = async (userId) => {
    if (!window.confirm("Demote this user from admin? They will lose user management access.")) return;
    try {
      const res = await apiFetch(`${apiBase}/api/admin/users/${userId}/demote-admin`, {
        method: 'POST'
      });
      if (res.ok) {
        fetchUsers();
      }
    } catch (err) {
      console.error("Failed to demote user", err);
    }
  };

  return (
    <Box sx={{ py: 4 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 800 }}>User Management</Typography>
        <Button startIcon={<RefreshIcon />} onClick={fetchUsers}>Refresh</Button>
      </Stack>

      <TableContainer component={Paper} sx={{ borderRadius: '16px' }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Email</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Role</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Joined</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }} align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} align="center" sx={{ py: 10 }}>
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : users.map((user) => (
              <TableRow key={user.id} hover>
                <TableCell>{user.email}</TableCell>
                <TableCell>
                  {user.is_approved ? (
                    <Chip label="Approved" color="success" size="small" />
                  ) : (
                    <Chip label="Pending" color="warning" size="small" variant="outlined" />
                  )}
                </TableCell>
                <TableCell>
                  {user.is_admin ? (
                    <Chip label="Admin" color="primary" size="small" />
                  ) : (
                    <Chip label="User" size="small" variant="outlined" />
                  )}
                </TableCell>
                <TableCell>
                  {new Date(user.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell align="right">
                  {!user.is_approved && (
                    <Tooltip title="Approve User">
                      <IconButton onClick={() => handleApprove(user.id)} color="success" size="small">
                        <ApproveIcon />
                      </IconButton>
                    </Tooltip>
                  )}
                  {!user.is_admin ? (
                    <Tooltip title="Promote to Admin">
                      <IconButton onClick={() => handlePromoteAdmin(user.id)} color="info" size="small">
                        <PromoteIcon />
                      </IconButton>
                    </Tooltip>
                  ) : (
                    <Tooltip title="Demote from Admin">
                      <IconButton onClick={() => handleDemoteAdmin(user.id)} color="warning" size="small">
                        <DemoteIcon />
                      </IconButton>
                    </Tooltip>
                  )}
                  {!user.is_admin && (
                    <Tooltip title="Delete User">
                      <IconButton onClick={() => handleDelete(user.id)} color="error" size="small">
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
