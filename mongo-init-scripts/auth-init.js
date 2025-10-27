db = db.getSiblingDB('auth_db');
db.createUser({
  user: 'auth_user',
  pwd: 'auth_password',
  roles: [{ role: 'readWrite', db: 'auth_db' }]
});

db.createUser({
  user: 'admin',
  pwd: 'securepassword123',
  roles: [{ role: 'dbAdmin', db: 'auth_db' }, { role: 'readWrite', db: 'auth_db' }]
});