

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-lyhnb9r1.us', // the auth0 domain prefix
    audience: 'http://localhost:5000', // the audience set for the auth0 app
    clientId: 'sqEFJ81TPURU7xJ1gZNG7k1ERmKNLBG0', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8104'
    // callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
