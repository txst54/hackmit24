import { MongoClient } from 'mongodb';

let client;
let clientPromise;

const uri = process.env.MONGODB_URI;

if (!uri) {
  throw new Error('Please add your MongoDB URI to .env.local');
}

if (!client) {
  client = new MongoClient(uri);
  clientPromise = client.connect();
}

export default clientPromise;
