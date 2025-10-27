db = db.getSiblingDB('content_db');
db.createUser({
  user: 'content_user',
  pwd: 'content_password',
  roles: [{ role: 'readWrite', db: 'content_db' }]
});

db.createUser({
  user: 'admin',
  pwd: 'securepassword123', 
  roles: [{ role: 'dbAdmin', db: 'content_db' }, { role: 'readWrite', db: 'content_db' }]
});