document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('form').onsubmit = send_email;

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#view-email').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function send_email() {
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
    })
  })
  .then(response => response.json())
  .then(result => {
    console.log(result);
  });
  localStorage.clear()
  load_mailbox('sent');
  return false;
}

function reply(email) {
  console.log('Replying to email')
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#view-email').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  fetch(`/emails/${email}`)
  .then(response => response.json())
  .then(email => {
    console.log(email);
    document.querySelector('#compose-recipients').value = email.sender;
    if (email.subject.indexOf('Re: ') === -1) {
      email.subject = `Re: ${email.subject}`;
    }
    document.querySelector('#compose-subject').value = email.subject;
    document.querySelector('#compose-body').value = `On ${email.timestamp}, ${email.sender} wrote: ${email.body}\n\nReply: `;
  });
}

function show_email(email, mailbox) {
  const email_div = document.createElement('div');
  email_div.className = 'row';

  const recipient = document.createElement('div');
  recipient.className = 'col-lg-2 col-md-3 col-sm-12';
  if (mailbox === 'sent') {
    recipient.innerHTML = email.recipients[0];
  } else {
    recipient.innerHTML = email.sender;
  }
  email_div.append(recipient);

  const subject = document.createElement('div');
  subject.className = 'col-lg-6 col-md-5 col-sm-12';
  subject.innerHTML = email.subject;
  email_div.append(subject);

  const timestamp = document.createElement('div');
  timestamp.className = 'col-lg-3 col-md-3 col-sm-12';
  timestamp.innerHTML = email.timestamp;
  email_div.append(timestamp);

  const archive_button = document.createElement('button');
  archive_button.className = 'btn btn-primary';
  if (mailbox === 'inbox') {
    archive_button.innerHTML = 'Archive'
  } else if (mailbox === 'archive') {
    archive_button.innerHTML = 'Inbox'
  }
  email_div.append(archive_button);
  if (mailbox === 'sent') {
    archive_button.style.display = 'none';
  } else {
    archive_button.style.display = 'block';
  }
  
  const card = document.createElement('div');
  if (email.read) {
    card.className = 'read_email'
  } else {
    card.className = 'unread_email'
  }
  card.append(email_div);

  document.querySelector('#emails-view').append(card);
  recipient.addEventListener('click', () => {
    console.log('Element has been clicked');
    view_email(email.id);
  });
  subject.addEventListener('click', () => {
    console.log('Element has been clicked');
    view_email(email.id);
  });
  timestamp.addEventListener('click', () => {
    console.log('Element has been clicked');
    view_email(email.id);
  });
  archive_button.addEventListener('click', () => {
    console.log('Element has been clicked');
    archive_email(email.id, mailbox);
  });

}

function archive_email(id, mailbox) {
  if (mailbox === 'inbox') {
    fetch(`/emails/${id}`, {
      method: 'PUT',
      body: JSON.stringify({
        archived: true
      })
    })
  } else if (mailbox === 'archive') {
    fetch(`/emails/${id}`, {
      method: 'PUT',
      body: JSON.stringify({
        archived: false
      })
    })
  }
  localStorage.clear();
  window.location.reload();
  return false;
}

function view_email(id) {
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#view-email').style.display = 'block';
  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
    console.log(email);
    document.querySelector('#sender').innerHTML = `<h4>From: ${email.sender}</h4>`;
    document.querySelector('#recipient').innerHTML = `<h4>To: ${email.recipients[0]}</h4>`;
    document.querySelector('#subject').innerHTML = `<h4>Subject: ${email.subject}</h4>`;
    document.querySelector('#timestamp').innerHTML = `<h4>Timestamp: ${email.timestamp}</h4>`;
    document.querySelector('#body').innerHTML = `<p>${email.body}</p>`;
  });
  read(id);
  document.querySelector('#reply').addEventListener('click', () => {
    console.log('Element has been clicked');
    reply(id);
  });

  return false;
  
}

function read(email) {
  fetch(`/emails/${email}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  })
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#view-email').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Show emails
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    console.log(emails)
    emails.forEach(email => show_email(email, mailbox)) 
  });
}