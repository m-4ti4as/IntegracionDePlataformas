const CAMPO = {
  nombre: 'Nombre y apellido',
  wsp: 'WhatsApp',
  email: 'Correo electrónico',
  canal: '¿Por qué red social nos hablaste?',
  tipoMascota: 'Tu mascota es',
  mascota: 'Su nombre',
  cumple: 'Su cumpleaños'
};

// Ejecutar una vez desde el editor en la cuenta de Peluditos.
function crearFormulario() {
  const properties = PropertiesService.getScriptProperties();
  const existente = properties.getProperty('FORM_ID');
  if (existente) {
    mostrarEnlaces_(FormApp.openById(existente));
    return;
  }
  const form = FormApp.create('Peluditos Pet Chile · Registro de interesados', false);
  form.setDescription('Cuéntanos sobre tu mascota para que podamos contactarte sobre tu torta y el cupón del 10%.');
  form.setCollectEmail(false);
  form.setLimitOneResponsePerUser(false);
  form.setAllowResponseEdits(false);
  form.setPublishingSummary(false);
  form.setConfirmationMessage('¡Gracias por registrarte! Peluditos se pondrá en contacto contigo.');
  const items = {};
  items.nombre = form.addTextItem().setTitle(CAMPO.nombre).setRequired(true);
  items.wsp = form.addTextItem().setTitle(CAMPO.wsp).setRequired(true);
  items.email = form.addTextItem().setTitle(CAMPO.email).setRequired(true)
    .setValidation(FormApp.createTextValidation().requireTextIsEmail().build());
  items.canal = form.addListItem().setTitle(CAMPO.canal).setRequired(true)
    .setChoiceValues(['Instagram', 'WhatsApp', 'Facebook', 'TikTok']);
  items.tipoMascota = form.addListItem().setTitle(CAMPO.tipoMascota).setRequired(true)
    .setChoiceValues(['Perro', 'Gato']);
  items.mascota = form.addTextItem().setTitle(CAMPO.mascota).setRequired(true);
  items.cumple = form.addDateItem().setTitle(CAMPO.cumple).setRequired(true).setIncludesYear(true)
    .setHelpText('Solo importan el día y el mes para el aviso anual.');
  const ids = Object.fromEntries(Object.entries(items).map(([key, item]) => [key, item.getId()]));
  properties.setProperties({ FORM_ID: form.getId(), ITEM_IDS: JSON.stringify(ids) });
  mostrarEnlaces_(form);
}

function mostrarEnlaces_(form) {
  console.log('Editar y publicar: ' + form.getEditUrl());
  console.log('Enlace para responder: ' + form.getPublishedUrl());
}

// Esta aplicación web solo devuelve respuestas a quien conoce la clave dedicada.
function doPost(event) {
  try {
    const input = JSON.parse(event.postData.contents);
    const properties = PropertiesService.getScriptProperties();
    const clave = properties.getProperty('SYNC_KEY');
    if (!clave || clave.length < 32 || !coincide_(input.clave, clave)) return json_({ ok: false });
    const form = FormApp.openById(properties.getProperty('FORM_ID'));
    const ids = JSON.parse(properties.getProperty('ITEM_IDS'));
    const fecha = Number.isSafeInteger(input.fechaMs) && input.fechaMs > 0 ? input.fechaMs : 0;
    const id = typeof input.respuesta === 'string' ? input.respuesta : '';
    const limite = Math.min(30, Math.max(1, Number.parseInt(input.limite, 10) || 30));
    const recientes = fecha ? form.getResponses(new Date(fecha - 1)) : form.getResponses();
    const respuestas = recientes.map(response => ({
      id: response.getId(), fechaMs: response.getTimestamp().getTime(), response
    })).filter(row => row.fechaMs > fecha || (row.fechaMs === fecha && row.id > id))
      .sort((a, b) => a.fechaMs - b.fechaMs || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
    const campos = Object.fromEntries(Object.entries(ids).map(([key, value]) => [value, key]));
    const lote = respuestas.slice(0, limite).map(row => {
      const datos = { id: row.id, fechaMs: row.fechaMs };
      for (const respuesta of row.response.getItemResponses()) {
        const campo = campos[respuesta.getItem().getId()];
        if (!campo) continue;
        const valor = respuesta.getResponse();
        datos[campo] = valor instanceof Date
          ? Utilities.formatDate(valor, Session.getScriptTimeZone(), 'yyyy-MM-dd')
          : String(valor || '');
      }
      return datos;
    });
    return json_({ ok: true, formId: form.getId(), respuestas: lote, hayMas: respuestas.length > limite });
  } catch (error) {
    return json_({ ok: false });
  }
}

function coincide_(input, clave) {
  if (typeof input !== 'string' || input.length !== clave.length) return false;
  let diferencia = 0;
  for (let i = 0; i < clave.length; i++) diferencia |= input.charCodeAt(i) ^ clave.charCodeAt(i);
  return diferencia === 0;
}

function json_(data) {
  return ContentService.createTextOutput(JSON.stringify(data)).setMimeType(ContentService.MimeType.JSON);
}
