db = db.getSiblingDB('notification_db');
db.createUser({
  user: 'notification_user',
  pwd: 'notification_password',
  roles: [{ role: 'readWrite', db: 'notification_db' }]
});

db.createUser({
  user: 'admin',
  pwd: 'securepassword123',
  roles: [{ role: 'dbAdmin', db: 'notification_db' }, { role: 'readWrite', db: 'notification_db' }]
});