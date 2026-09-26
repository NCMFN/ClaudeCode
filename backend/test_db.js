const { Client } = require('pg');

const client = new Client({
  connectionString: 'postgres://postgres:postgres@localhost:5432/roots'
});

client.connect()
  .then(() => console.log('Connected'))
  .catch(e => console.error('Connection error', e.stack))
  .finally(() => client.end());
