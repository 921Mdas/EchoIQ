import React, {useState, useEffect} from 'react'
import { Avatar, Typography, Box } from '@mui/material';

import './Nav.scss'

// icons import
import DataUsageIcon from '@mui/icons-material/DataUsage';

// logo
const Logo = ()=>{
  return <div className='logo'>
     <span className='logo_icon'><DataUsageIcon /></span> 
    <span className='logo_text'>921IQ</span>
  </div>
}

// user session info

const UserSession = () => {
const [user, setUser] = useState({
  full_name: '',
  avatarUrl: 'https://i.pravatar.cc/150?img=8', // default avatar
});

useEffect(() => {
  const storedName = localStorage.getItem('fullname');
  if (storedName) {
    setUser((prev) => ({
      ...prev,
      full_name: storedName,
    }));
  }
}, []);

  return (
    <div className="user">
    <Box
      display="flex"
      alignItems="center"
      gap={2}
      sx={{
        padding: '0.2em 1rem',
        borderRadius: '8px',
      }}
    >
      <Avatar src={user.avatarUrl} alt={user.full_name} />

      <Typography variant="body1" fontWeight="900">
  {user.full_name}
</Typography>
    </Box>
    </div>
  );
};

const Nav = () => {
  return (
    <div className='Nav'>
      <Logo />
      <UserSession />
    </div>
  )
}

export default Nav