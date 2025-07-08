// Simple localStorage-based user and script management
const STORAGE_USERS = 'tp_users';
const STORAGE_CURRENT = 'tp_current_user';

function loadUsers(){
  return JSON.parse(localStorage.getItem(STORAGE_USERS) || '{}');
}
function saveUsers(users){
  localStorage.setItem(STORAGE_USERS, JSON.stringify(users));
}
function getCurrentUser(){
  return localStorage.getItem(STORAGE_CURRENT);
}
function setCurrentUser(u){
  localStorage.setItem(STORAGE_CURRENT, u);
}
function loadScripts(user){
  return JSON.parse(localStorage.getItem('tp_scripts_'+user) || '[]');
}
function saveScripts(user, arr){
  localStorage.setItem('tp_scripts_'+user, JSON.stringify(arr));
}

// Registration
function register(event){
  event.preventDefault();
  const form=event.target;
  const username=form.username.value.trim();
  const password=form.password.value;
  if(!username||!password) return;
  const users=loadUsers();
  if(users[username]){ alert('User already exists'); return; }
  users[username]={password};
  saveUsers(users);
  alert('Registered! Please log in.');
  location.href='login.html';
}

function login(event){
  event.preventDefault();
  const form=event.target;
  const username=form.username.value.trim();
  const password=form.password.value;
  const users=loadUsers();
  if(users[username]&&users[username].password===password){
    setCurrentUser(username);
    location.href='dashboard.html';
  }else{
    alert('Invalid credentials');
  }
}

function logout(){
  localStorage.removeItem(STORAGE_CURRENT);
  location.href='login.html';
}

// Dashboard rendering
function renderDashboard(){
  const user=getCurrentUser();
  if(!user){location.href='login.html';return;}
  document.getElementById('welcome').textContent=user;
  const list=document.getElementById('scriptList');
  const scripts=loadScripts(user);
  list.innerHTML='';
  if(!scripts.length){
    list.innerHTML='<tr><td colspan="2">No scripts yet.</td></tr>';
  }else{
    scripts.forEach(s=>{
      const tr=document.createElement('tr');
      tr.innerHTML=`<td>${s.title}</td><td><a href="teleprompter.html?id=${s.id}">Open</a></td>`;
      list.appendChild(tr);
    });
  }
}

function saveScript(event){
  event.preventDefault();
  const form=event.target;
  const title=form.title.value.trim();
  const body=form.body.value;
  const user=getCurrentUser();
  const scripts=loadScripts(user);
  if(scripts.length>=20){ alert('Max 20 scripts allowed'); return; }
  const id=Date.now();
  scripts.push({id,title,body});
  saveScripts(user,scripts);
  location.href='dashboard.html';
}

// Load script into teleprompter
function loadTeleprompter(){
  const params=new URLSearchParams(location.search);
  const id=parseInt(params.get('id'));
  const user=getCurrentUser();
  const scripts=loadScripts(user);
  const script=scripts.find(s=>s.id===id);
  if(!script){alert('Script not found'); location.href='dashboard.html'; return;}
  document.getElementById('scriptInput').value=script.body;
}

// Live session using localStorage events
function initLiveInput(){
  const id=Date.now().toString(36);
  document.getElementById('shareLink').value=location.origin+location.pathname.replace('live_input.html','live_display.html')+'?id='+id;
  const ta=document.getElementById('liveText');
  function send(){ localStorage.setItem('tp_live_'+id, ta.value); }
  ta.addEventListener('input', ()=>send());
}

function initLiveDisplay(){
  const params=new URLSearchParams(location.search);
  const id=params.get('id');
  const disp=document.getElementById('display');
  function update(){ disp.textContent=localStorage.getItem('tp_live_'+id)||''; }
  window.addEventListener('storage', e=>{ if(e.key==='tp_live_'+id) update(); });
  update();
}
