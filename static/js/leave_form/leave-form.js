
const leaveData = document.getElementById('leave-data');
var CURRENT_UID         = document.getElementById('current-uid').value;
var SAVE_ROW_URL        = "/leave/save-row";
var ADD_ROW_URL         = "/leave/add";
var DELETE_ROW_BASE_URL = "/leave/delete/";
const CARRY_OVER =
    parseFloat(leaveData.dataset.carryOver) || 0;

const ENTITLE_CONTRACT =
    parseFloat(leaveData.dataset.entitleContract) || 0;

const TOTAL_AVAIL =
    parseFloat(leaveData.dataset.totalAvail || 0);
var selectedRow         = null;
const metaEl = document.getElementById('employee-meta');

const FULL_NAME = metaEl.dataset.fullName;
const JOB_TITLE = metaEl.dataset.jobTitle;
const DEPARTMENT = metaEl.dataset.department;
const WORKING_LOCATION = metaEl.dataset.workingLocation;
const REPORT_TO = metaEl.dataset.reportTo;
const JOINING_DATE = metaEl.dataset.joiningDate;

/* ── Helper: get leave type value from a row ── */
function getLeaveType(row) {
  var sel = row.querySelector('.leave-type-sel');
  if (sel) return sel.value;
  return row.dataset.leaveType || '';
}

/* ── Balance: only annual + annual_carry count ── */
function updateBalance() {
  var total = 0;
  document.querySelectorAll('.leave-row').forEach(function(row) {
    var badge = row.querySelector('.status-badge');
    if (badge && badge.classList.contains('status-rejected')) return;
    var lt = getLeaveType(row);
    if (lt !== 'annual' && lt !== 'annual_carry') return;
    var inp = row.querySelector('.days-input');
    if (inp) total += parseFloat(inp.value) || 0;
  });
  var balance = TOTAL_AVAIL - total;
  function set(id, val) { var el = document.getElementById(id); if (el) el.textContent = val; }
  set('total-days', total);
  set('al-used-val', total);
  set('remaining-val', balance);
  set('tfoot-balance', balance);
  var tb = document.getElementById('tfoot-balance');
  if (tb) tb.className = balance < 0 ? 'bal-negative' : 'bal-positive';
}

/* ── Excel export ── */
function downloadExcel() {
  var leaveTypeLabel = {
    'annual_carry':'AL — Annual Leave (Carry Over)', 'annual':'AL — Annual Leave (Advanced)',
    'sick':'SL — Sick Leave', 'maternity':'Me L — Maternity Leave',
    'marriage':'Ma L — Marriage Leave', 'paternity':'Pa L — Paternity Leave',
    'personal':'Per L — Personal Leave', 'compensate':'Co L — Compensatory Leave',
    'unpaid':'Un L — Unpaid Leave',
  };
  var infoData = [
    ['INDIVIDUAL LEAVE RECORD — TOI-AHR-LR-F01/NOV15'],[],
    ['Full Name', FULL_NAME, 'Year', '2026'],
    ['Job Title', JOB_TITLE, 'Department', DEPARTMENT],
    ['Working Location', WORKING_LOCATION, 'Reports To', REPORT_TO],
    ['Joining Date', JOINING_DATE],[],
    ['ANNUAL LEAVE BALANCE'],
    ['Carry Over','Contracted Entitlement','Total Available','AL Used','Remaining'],
    [
      CARRY_OVER,
      ENTITLE_CONTRACT,
      TOTAL_AVAIL,
      parseFloat(
          document.getElementById('al-used-val')?.textContent || 0
      ),
      parseFloat(
          document.getElementById('remaining-val')?.textContent || 0
      )
    ]];
  var rows = [['No.','Date From','Date To','Leave Type','Days','Notes','Status']];
  document.querySelectorAll('#leave-tbody .leave-row').forEach(function(row, idx) {
    var typeEl = row.querySelector('.leave-type-sel');
    var statusBadge = row.querySelector('.status-badge');
    var typeVal = typeEl ? (leaveTypeLabel[typeEl.value] || typeEl.value)
                        : (row.querySelector('.fval') ? row.querySelector('.fval').textContent.trim() : '');
    rows.push([idx+1,
      (document.getElementById('date-from-'+row.dataset.id)||{}).value||'',
      (document.getElementById('date-to-'+row.dataset.id)||{}).value||'',
      typeVal,
      parseFloat((document.getElementById('days-'+row.dataset.id)||{}).value)||0,
      (document.getElementById('notes-'+row.dataset.id)||{}).value||'',
      statusBadge ? statusBadge.textContent.trim() : '',
    ]);
  });
  rows.push([]);
  rows.push(['','','','Total Days Used', parseFloat(document.getElementById('total-days').textContent)||0]);
  rows.push(['','','','Annual Leave Balance', parseFloat(document.getElementById('tfoot-balance').textContent)||0]);
  var wb = XLSX.utils.book_new();
  var wsInfo = XLSX.utils.aoa_to_sheet(infoData); wsInfo['!cols']=[{wch:22},{wch:28},{wch:20},{wch:28}];
  XLSX.utils.book_append_sheet(wb, wsInfo, 'Employee Info');
  var wsLeave = XLSX.utils.aoa_to_sheet(rows); wsLeave['!cols']=[{wch:5},{wch:13},{wch:13},{wch:32},{wch:7},{wch:24},{wch:14}];
  XLSX.utils.book_append_sheet(wb, wsLeave, 'Leave Records');
  XLSX.writeFile(
    wb,
        `MyLeaveRecord_${FULL_NAME || 'Employee'}_2026.xlsx`
            .replace(/\s+/g, '_')
    );
}

/* ── PDF export ── */
function downloadPDF() {
  var el = document.querySelector('.ilr-card');
  document.querySelectorAll('.ilr-table-toolbar').forEach(function(t){ t.style.display='none'; });
  document.querySelectorAll('.btn-sign').forEach(function(b){ b.style.display='none'; });
  document.querySelectorAll('.sign-print-box').forEach(function(b){ b.style.display='block'; });
  document.querySelectorAll('.inp-select').forEach(function(s){ s.style.display='none'; });
  document.querySelectorAll('.td-type .fval').forEach(function(f){ f.style.display='inline'; });
  document.querySelectorAll('.th-approval-status,.td-approval-status').forEach(function(e){ e.style.display='none'; });
  document.querySelectorAll('.inp-notes').forEach(function(inp){
    var div=document.createElement('div'); div.className='notes-pdf-div';
    div.style.cssText='font-size:10px;word-break:break-word;white-space:normal;border-bottom:1px solid #ccc;min-height:18px;padding:2px 0;width:100%;background:transparent;font-family:inherit;color:#111;';
    div.textContent=inp.value||''; inp.style.display='none'; inp.parentNode.insertBefore(div,inp);
  });
  document.querySelectorAll('.inp-date').forEach(function(inp){
    var div=document.createElement('div'); div.className='date-pdf-div';
    div.style.cssText='font-size:10px;border-bottom:1px solid #ccc;display:inline-block;min-width:80px;background:transparent;font-family:inherit;color:#111;';
    div.textContent=inp.value||''; inp.style.display='none'; inp.parentNode.insertBefore(div,inp);
  });
  document.querySelectorAll('.inp-days').forEach(function(inp){
    var div=document.createElement('div'); div.className='days-pdf-div';
    div.style.cssText='font-size:11px;border-bottom:1px solid #ccc;text-align:center;min-width:32px;background:transparent;font-family:inherit;color:#111;display:inline-block;';
    div.textContent=inp.value||'0'; inp.style.display='none'; inp.parentNode.insertBefore(div,inp);
  });
  el.style.paddingBottom='40px';
  var opt={
    margin:[8,8,14,8],
    filename:'MyLeaveRecord_{{ meta.full_name or "Employee" }}_2026.pdf'.replace(/\s+/g,'_'),
    image:{type:'jpeg',quality:0.98},
    html2canvas:{scale:2,useCORS:true,letterRendering:true,scrollY:0},
    jsPDF:{unit:'mm',format:'a4',orientation:'landscape'},
    pagebreak:{mode:'css',avoid:'.leave-row, tfoot, .ilr-balance'}
  };
  html2pdf().set(opt).from(el).save().then(function(){
    document.querySelectorAll('.btn-sign').forEach(function(b){ b.style.display=''; });
    document.querySelectorAll('.sign-print-box').forEach(function(b){ b.style.display=''; });
    document.querySelectorAll('.inp-select').forEach(function(s){ s.style.display=''; });
    document.querySelectorAll('.td-type .fval').forEach(function(f){ f.style.display='none'; });
    document.querySelectorAll('.th-approval-status,.td-approval-status').forEach(function(e){ e.style.display=''; });
    document.querySelectorAll('.inp-notes,.inp-date,.inp-days').forEach(function(inp){ inp.style.display=''; });
    document.querySelectorAll('.notes-pdf-div,.date-pdf-div,.days-pdf-div').forEach(function(d){ d.remove(); });
    document.querySelectorAll('.ilr-table-toolbar').forEach(function(t){ t.style.display=''; });
    el.style.paddingBottom='';
  });
}

/* ── Signature modal ── */
var _sigCtx, _sigDrawing=false, _sigEntryId='';
function openSigModal(entryId, rowIndex) {
  _sigEntryId=entryId;
  document.getElementById('sig-modal-title').textContent='Applicant Signature — Row '+rowIndex;
  document.getElementById('sig-modal').style.display='flex';
  var canvas=document.getElementById('sig-canvas');
  canvas.width=Math.min(canvas.parentElement.clientWidth,512);
  _sigCtx=canvas.getContext('2d');
  _sigCtx.clearRect(0,0,canvas.width,canvas.height);
  _sigCtx.strokeStyle='#2c2218'; _sigCtx.lineWidth=2; _sigCtx.lineCap='round'; _sigCtx.lineJoin='round';
  canvas.onmousedown =function(e){_sigDrawing=true;_sigCtx.beginPath();_sigCtx.moveTo.apply(_sigCtx,_pos(canvas,e));};
  canvas.onmousemove =function(e){if(!_sigDrawing)return;_sigCtx.lineTo.apply(_sigCtx,_pos(canvas,e));_sigCtx.stroke();};
  canvas.onmouseup   =function(){_sigDrawing=false;};
  canvas.onmouseleave=function(){_sigDrawing=false;};
  canvas.ontouchstart=function(e){e.preventDefault();_sigDrawing=true;_sigCtx.beginPath();_sigCtx.moveTo.apply(_sigCtx,_pos(canvas,e.touches[0]));};
  canvas.ontouchmove =function(e){e.preventDefault();if(!_sigDrawing)return;_sigCtx.lineTo.apply(_sigCtx,_pos(canvas,e.touches[0]));_sigCtx.stroke();};
  canvas.ontouchend  =function(){_sigDrawing=false;};
}
function _pos(canvas,e){var r=canvas.getBoundingClientRect();return[e.clientX-r.left,e.clientY-r.top];}
function clearSigCanvas(){var c=document.getElementById('sig-canvas');_sigCtx.clearRect(0,0,c.width,c.height);}
function closeSigModal(){document.getElementById('sig-modal').style.display='none';}
function confirmSig(){
  var dataUrl=document.getElementById('sig-canvas').toDataURL('image/png');
  var hidden=document.getElementById('applicant-sig-'+_sigEntryId);
  if(hidden) hidden.value=dataUrl;
  var btn=document.querySelector('[data-entry="'+_sigEntryId+'"][data-role="applicant"]');
  if(btn){
    btn.parentElement.innerHTML=
      '<div class="signed-display">'+
        '<img src="'+dataUrl+'" class="sig-img" alt="Signed" style="cursor:pointer;max-width:100px;max-height:36px;"'+
             ' onclick="openSigModal(\''+_sigEntryId+'\',\'?\')">'+
      '</div>'+
      '<input type="hidden" id="applicant-sig-'+_sigEntryId+'" value="'+dataUrl+'">'+
      '<div class="sign-print-box" style="display:none;"></div>';
  }
  closeSigModal();
}

/* ── Add row ── */
function addRow(){
  var fd=new FormData();
  fd.append('csrf_token',document.getElementById('csrf-token').value);
  fd.append('leave_type','annual'); fd.append('days','0');
  fd.append('date_from',new Date().toISOString().slice(0,10));
  fd.append('date_to',  new Date().toISOString().slice(0,10));
  fd.append('notes','');
  fd.append('carry_over',CARRY_OVER);
  fd.append('entitle_contract',ENTITLE_CONTRACT);
  fd.append('target_uid',CURRENT_UID);
  fetch(ADD_ROW_URL,{method:'POST',body:fd}).then(function(r){return r.json();}).then(function(d){
    if(!d.ok){

        showToast(
            d.error || 'Create failed.',
            'error'
        );

        return;
    }

    showToast(
        d.message || 'Created successfully.',
        'success'
    );
    var id=d.id, tbody=document.getElementById('leave-tbody');
    var rowCount=tbody.rows.length+1;
    var tr=tbody.insertRow();
    tr.className='leave-row'; tr.dataset.id=id; tr.dataset.saved='true'; tr.dataset.leaveType='annual';
    tr.innerHTML=
      '<td class="td-no">'+rowCount+'</td>'+
      '<td class="td-date"><div class="date-range">'+
        '<input type="date" class="inp-date" id="date-from-'+id+'" value="'+new Date().toISOString().slice(0,10)+'">'+
        '<span class="date-sep">–</span>'+
        '<input type="date" class="inp-date" id="date-to-'+id+'" value="'+new Date().toISOString().slice(0,10)+'">'+
      '</div></td>'+
      '<td class="td-type">'+
        '<select class="inp-select leave-type-sel" id="leave-type-'+id+'"'+
                ' onchange="this.closest(\'tr\').dataset.leaveType=this.value; updateBalance();">'+
          '<option value="">— select type —</option>'+
          '<option value="annual_carry">AL — Annual Leave (Carry Over)</option>'+
          '<option value="annual" selected>AL — Annual Leave (Advanced)</option>'+
          '<option value="sick">SL — Sick Leave</option>'+
          '<option value="maternity">Me L — Maternity Leave</option>'+
          '<option value="marriage">Ma L — Marriage Leave</option>'+
          '<option value="paternity">Pa L — Paternity Leave</option>'+
          '<option value="personal">Per L — Personal Leave</option>'+
          '<option value="compensate">Co L — Compensatory Leave</option>'+
          '<option value="unpaid">Un L — Unpaid Leave</option>'+
        '</select>'+
        '<span class="fval" style="display:none;">AL — Annual Leave (Advanced)</span>'+
      '</td>'+
      '<td class="td-days"><input type="number" min="0" step="0.5" value="0" class="inp-days days-input" id="days-'+id+'"></td>'+
      '<td class="td-notes"><textarea class="inp-notes" placeholder="Add note…" id="notes-'+id+'" rows="1"></textarea></td>'+
      '<td class="td-sign">'+
        '<button type="button" class="btn-sign no-print" data-entry="'+id+'" data-role="applicant"'+
                ' onclick="openSigModal(\''+id+'\','+rowCount+')">'+
          '<i class="bi bi-pen"></i> Sign'+
        '</button>'+
        '<input type="hidden" id="applicant-sig-'+id+'" value="">'+
        '<div class="sign-print-box"></div>'+
      '</td>'+
      '<td class="td-approval-status"><span class="status-badge status-pending">⏳ Pending</span></td>';
    tr.addEventListener('click',function(){
      document.querySelectorAll('.leave-row').forEach(function(r){r.classList.remove('selected-row');});
      this.classList.add('selected-row'); selectedRow=this;
    });
    attachDateListeners(tr);
    var textarea=tr.querySelector('.inp-notes');
    if(textarea){autoResizeTextarea(textarea);textarea.addEventListener('input',function(){autoResizeTextarea(this);});}
    tr.querySelector('.days-input').addEventListener('input',updateBalance);
    updateBalance();
  }).catch(function(err){
        showToast(
            'Connection error.',
            'error'
        );
    });
}

/* ── Delete selected row ── */
function deleteLastRow(){
    if(!selectedRow){
        showToast(
            'Please select a row to delete.',
            'error'
        );
        return;
    }
    var statusBadge =
        selectedRow.querySelector('.status-badge');
    if(
        statusBadge &&
        (
            statusBadge.classList.contains('status-approved')
            ||
            selectedRow.classList.contains('row-approved')
        )
    ){
        showToast(
            'Approved rows cannot be deleted.',
            'error'
        );
        return;
    }
    if(
        !confirm(
            'Are you sure you want to delete this row?'
        )
    ){
        return;
    }
    var rowId = selectedRow.dataset.id;
    if(rowId){
        var fd = new FormData();
        fd.append(
            'csrf_token',
            document.getElementById('csrf-token').value
        );
        fd.append(
            'target_uid',
            CURRENT_UID
        );
        fetch(
            DELETE_ROW_BASE_URL + rowId,
            {
                method:'POST',
                headers:{
                    'X-CSRFToken':
                        document.getElementById(
                            'csrf-token'
                        ).value
                },
                body:fd
            }
        )
        .then(function(r){
            return r.json();
        })
        .then(function(d){
            if(d.ok){
                removeRowFromDOM();
                showToast(
                    d.message ||
                    'Leave request deleted successfully.',
                    'success'
                );

            }else{
                showToast(
                    d.error ||
                    'Failed to delete row.',
                    'error'
                );
            }
        })
        .catch(function(err){
            console.error(err);
            showToast(
                'Connection error.',
                'error'
            );
        });
    }else{
        removeRowFromDOM();
        showToast(
            'Row deleted successfully.',
            'success'
        );
    }
}

function removeRowFromDOM(){
  selectedRow.remove(); selectedRow=null;
  document.querySelectorAll('#leave-tbody .leave-row').forEach(function(row,idx){
    var td=row.querySelector('.td-no'); if(td) td.textContent=idx+1;
  });
  updateBalance();
}

/* ── Save / Submit ── */
function savePendingRows(){
    console.log("savePendingRows called");
  var rows=document.querySelectorAll('.leave-row:not(.row-approved)');
  if(!rows.length){alert('No pending rows to save.');return;}
  var csrf=document.getElementById('csrf-token').value;
  var promises=Array.from(rows).map(function(row){
    var id=row.dataset.id; if(!id) return Promise.resolve();
    var fd=new FormData();
    fd.append('csrf_token',csrf);
    fd.append('entry_id',id);
    fd.append('date_from',(document.getElementById('date-from-'+id)||{}).value||'');
    fd.append('date_to',(document.getElementById('date-to-'+id)||{}).value||'');
    fd.append('leave_type',(document.getElementById('leave-type-'+id)||{}).value||'');
    fd.append('days',(document.getElementById('days-'+id)||{}).value||0);
    fd.append('notes',(document.getElementById('notes-'+id)||{}).value||'');
    fd.append('target_uid',CURRENT_UID);
    var sig=document.getElementById('applicant-sig-'+id); if(sig) fd.append('applicant_sig',sig.value);
    console.log({
        entry_id: id,
        leave_type: (document.getElementById('leave-type-'+id)||{}).value,
        days: (document.getElementById('days-'+id)||{}).value,
    });
    fetch(SAVE_ROW_URL,{
            method:'POST',
            body:fd
        })
        .then(r => r.json())
        .then(d => {

            if(d.ok){

                showToast(
                    d.message,
                    'success'
                );

            }else{

                showToast(
                    d.error,
                    'error'
                );

            }

        });
  });
  Promise.all(promises).then(function(){updateBalance();setTimeout(function(){location.reload();},300);})
    .catch(function(err){console.error(err);alert('Error saving.');});
}

/* ── Date / days calculation ── */
function calculateDays(fromDate,toDate){
  if(!fromDate||!toDate)return 0;
  var start=new Date(fromDate),end=new Date(toDate); if(end<start)return 0;
  var total=0,current=new Date(start);
  while(current<=end){
    var day=current.getDay();
    if(day===6) total+=0.5;
    else if(day!==0) total+=1;
    current.setDate(current.getDate()+1);
  }
  return total + 1;
}
function attachDateListeners(row){
  var f=row.querySelector('[id^="date-from-"]'),t=row.querySelector('[id^="date-to-"]'),d=row.querySelector('.days-input');
  if(!f||!t||!d)return;
  function upd(){d.value=calculateDays(f.value,t.value);updateBalance();}
  f.addEventListener('change',upd); t.addEventListener('change',upd);
}

/* ── Auto resize textarea ── */
function autoResizeTextarea(el){el.style.height='auto';el.style.height=el.scrollHeight+'px';}

/* ── beforePrint / afterPrint ── */
function beforePrint(){
  document.querySelectorAll('.ilr-table-toolbar').forEach(function(t){t.style.display='none';});
  document.querySelectorAll('.th-approval-status,.td-approval-status').forEach(function(e){e.style.display='none';});
  document.querySelectorAll('.inp-select').forEach(function(s){s.style.display='none';});
  document.querySelectorAll('.td-type .fval').forEach(function(f){f.style.display='inline';});
  document.querySelectorAll('.sign-print-box').forEach(function(b){b.style.display='block';});
  document.querySelectorAll('.btn-sign').forEach(function(b){b.style.display='none';});
  document.querySelectorAll('.inp-notes').forEach(function(inp){
    if(inp.nextSibling&&inp.nextSibling.classList&&inp.nextSibling.classList.contains('notes-print-div'))return;
    var div=document.createElement('div');div.className='notes-print-div';div.textContent=inp.value||'';
    inp.parentNode.insertBefore(div,inp.nextSibling);
  });
  document.querySelectorAll('.inp-date').forEach(function(inp){
    if(inp.nextSibling&&inp.nextSibling.classList&&inp.nextSibling.classList.contains('date-print-div'))return;
    var div=document.createElement('div');div.className='date-print-div';div.textContent=inp.value||'';
    inp.parentNode.insertBefore(div,inp.nextSibling);
  });
  document.querySelectorAll('.inp-days').forEach(function(inp){
    if(inp.nextSibling&&inp.nextSibling.classList&&inp.nextSibling.classList.contains('days-print-div'))return;
    var div=document.createElement('div');div.className='days-print-div';div.textContent=inp.value||'0';
    inp.parentNode.insertBefore(div,inp.nextSibling);
  });
}
function afterPrint(){
  document.querySelectorAll('.ilr-table-toolbar').forEach(function(t){t.style.display='';});
  document.querySelectorAll('.th-approval-status,.td-approval-status').forEach(function(e){e.style.display='';});
  document.querySelectorAll('.inp-select').forEach(function(s){s.style.display='';});
  document.querySelectorAll('.td-type .fval').forEach(function(f){f.style.display='none';});
  document.querySelectorAll('.sign-print-box').forEach(function(b){b.style.display='';});
  document.querySelectorAll('.btn-sign').forEach(function(b){b.style.display='';});
  document.querySelectorAll('.notes-print-div,.date-print-div,.days-print-div').forEach(function(d){d.remove();});
}

/* ── Init ── */
document.querySelectorAll('.leave-row').forEach(function(row){
  row.addEventListener('click',function(){
    document.querySelectorAll('.leave-row').forEach(function(r){r.classList.remove('selected-row');});
    this.classList.add('selected-row'); selectedRow=this;
  });
  attachDateListeners(row);
  var d=row.querySelector('.days-input'); if(d) d.addEventListener('input',updateBalance);
  var ta=row.querySelector('.inp-notes');
  if(ta){autoResizeTextarea(ta);ta.addEventListener('input',function(){autoResizeTextarea(this);});}
});
updateBalance();
window.addEventListener('beforeprint',beforePrint);
window.addEventListener('afterprint', afterPrint);
