function addMessage(title, subtitle, socket) {
    const text = '<div class="overflow-auto p-3 mb-3 mb-md-0 mr-md-3 bg-light">\
                                <div class="media">\
                                    <img class="mr-3" src="static/spyicon.jpg" alt="Generic placeholder image">\
                                    <div class="media-body">\
                                    <h5 class="mt-0">' + title+ '</h5>'
                                     + subtitle + '\
                                    </div>\
                                </div>\
                            </div>'
    socket.emit('message',{data: text});
}

function addWatcherMessage(title, subtitle, socket) {
    const text = '<div class="overflow-auto p-3 mb-3 mb-md-0 mr-md-3 bg-light">\
                                <div class="media">\
                                    <img class="mr-3" src="static/spyicon.jpg" alt="Generic placeholder image">\
                                    <div class="media-body">\
                                    <h5 class="mt-0">' + title+ '</h5>'
                                     + subtitle + '\
                                    </div>\
                                </div>\
                            </div>'
    socket.emit('watcher message', {data: text});
}

//game progression functions
function nightProgression(socket) {
    socket.emit('disable');
    const nightString = count.toString();
    socket.emit('show screen', {title: 'Night ' + nightString, subtitle: 'Mafia pick someone to kill..'});
    socket.emit('kill phase');
}

function killPhase(target, socket) {
    socket.emit('disable');
    document.getElementsByName('kill').disabled = true;
    socket.emit('kill', {name: target});
    const nightString = count.toString();
    socket.emit('show screen', {title: 'Night ' + nightString, subtitle: 'Doctor pick someone to save..'});
    socket.emit('save phase');
}

function savePhase(target, socket) {
    socket.emit('disable')
    document.getElementsByName('save').disabled = true;
    socket.emit('save', {name: target});
    const nightString = count.toString();
    socket.emit('show screen', {title: 'Night ' + nightString, subtitle: 'Detective pick someone to interrogate..'});
    socket.emit('detect phase');
}

function detectPhase(target, socket) { 
    socket.emit('disable')
    document.getElementsByName('detect').disabled = true;
    socket.emit('detect', {name: target});
    socket.emit('vote phase');
}

var count = 1;

$(document).ready(function() {
    const socket = io.connect('https://' + document.domain + ':' + location.port);
    socket.emit('sync users');
    $('.alert').hide();

    socket.on('show', function(msg) {
        $('#screenTitle').html(msg.title);
        $('#screenSub').html(msg.subtitle);
        $('#screen').modal('show');
    });

    socket.on('get name', function(){
        $('#modal').modal('show');
    });

    socket.on('update board', function(msg){
        const board = msg.board;
        $('#cards').html(board);
    });

    socket.on('update log', function(msg){
        const updated = msg.data;
        $('#log').html(updated);
    });

    socket.on('assign', function(message){
        const name = Object.keys(message)[0];
        const role = Object.values(message)[0];
        $('#'+ name+'_role').html(role);
    });

    socket.on('disable all', function(){
        $('a[name="kill"]').addClass('disabled');
        $('a[name="save"]').addClass('disabled');
        $('a[name="detect"]').addClass('disabled');
        $('a[name="hang"]').addClass('disabled');
        document.getElementById("night").disabled = true;
    });

    socket.on('kill enable', function(){
        $('a[name="kill"]').removeClass('disabled');
    });

    socket.on('save enable', function(){
        $('a[name="save"]').removeClass('disabled');
    });

    socket.on('detect enable', function(){
        $('a[name="detect"]').removeClass('disabled');
    });

    socket.on('enter kill phase', function(msg){
        killPhase(msg.name, socket);
    });

    socket.on('enter save phase', function(msg){
        savePhase(msg.name, socket);
    });

    socket.on('enter detect phase', function(msg){
        socket.emit('show screen', {title: 'Morning', subtitle: 'The night has ended'});
        detectPhase(msg.name, socket);
    });

    socket.on('reveal', function(msg){
        const name = msg.name;
        const role = msg.role;
        if (role == 'mafia'){
            $('#'+name+'_role').html(role);
        } else {
            $('#'+name+'_role').html('not mafia');
        }
    });

    socket.on('reveal actual', function(msg){
        const name = msg.name;
        const role = msg.role;
        $('#'+name+'_role').html(role);
    });

    socket.on('prevent start', function(){
        document.getElementById("start").disabled = true;
    });

    socket.on('night over', function(msg){
        const death = msg.deaths;
        console.log(death);
        if (death == ''){
        } else {
            $('#'+death+'_status').html('Status: Dead');
        }
        socket.emit('enable night');
    })

    socket.on('hang enable', function(){
        $('a[name="hang"]').removeClass('disabled');
        document.getElementById("night").disabled = false;
    });

    socket.on('death message', function(msg){
        var display = count;
        const display_string = display.toString();
        const death = msg.deaths
        if (death == ''){
            addMessage('Night ' + display_string, 'All live to see another day..', socket);
        } else {
            addMessage('Night ' + display_string, death + ' was killed', socket);
        }
        socket.emit('increment', {night: count});
    });

    socket.on('add count', function(msg){
        const track = msg.night;
        count = track;
    });

    socket.on('result', function(msg){
        const result = msg.winners;
        console.log(result);
        if (result == 'mafia'){
            addMessage('Mafia Win', 'The Mafia have overthrown the townspeople, all who remain were executed', socket);
            socket.emit('show screen', {
                title: 'Mafia Win', 
                subtitle: 'The Mafia have overthrown the townspeople, all who remain were executed'
            });

        } else {
            addMessage('Village Win', 'The Mafia have been weeded out and hanged', socket);
            socket.emit('show screen', {
                title: 'Village Win', 
                subtitle: 'The Mafia were hanged and their families were enslaved for compensation of the dead villagers'
            });
        }
        socket.emit('disable');
        socket.emit('disable start');
    });

    socket.on('hang disable', function(){
        $('a[name="hang"]').addClass('disabled');
    });

    socket.on('clear storage', function(){
        sessionStorage.clear();
    });

    $('#enter').click(function(){
        var Name = $('#name').val();
        var duplicate = false;
        var temp = '<div class="card" id="' +Name+'" style="width: 18rem;">\
                        <img src="static/spyicon.png" class="card-img-top" alt="...">\
                        <div class="card-body">\
                            <h5 class="card-title">' + Name + '</h5>\
                            <p class="card-text" id="' + Name+ '_status">Status: Alive</p>\
                            <p class="card-text" id="' + Name+ '_role">???</p>\
                            <a name="kill" id="'+Name+'_kill" class="btn btn-primary disabled">Kill</a>\
                            <a name="save" id="'+Name+'_save" class="btn btn-secondary disabled">Save</a>\
                            <a name="detect" id="'+Name+'_detect" class="btn btn-secondary disabled">Detect</a>\
                            <a name="hang" id="'+Name+'_hang" class="btn btn-secondary disabled">Hang</a>\
                        </div>\
                    </div>'
        $('.card').each(function(){
            if ($(this).attr("id") == Name) {
                console.log($(this).attr("id"));
                duplicate = true;
            }
        })
        if (!duplicate){
            $('#modal').modal('hide');
            socket.emit('join gamekey');
            socket.emit('board entry', {data: temp});
            socket.emit('add player', {name: $('#name').val()});
        } else {
            $('.alert').show();
        }
    });

    $(document).on("click", "a[name='kill']", function(){
        const name = $(this).attr('id').split("_")[0];
        addWatcherMessage('Kill Event', 'Mafia wants to kill ' + name, socket);
        socket.emit('kill check', {target: name});
    });

    $(document).on("click", "a[name='save']", function(){
        const name = $(this).attr('id').split("_")[0];
        addWatcherMessage('Save Event', 'Doctor wants to save ' + name, socket);
        socket.emit('save check', {target: name});
    });

    $(document).on("click", "a[name='detect']", function(){
        const name = $(this).attr('id').split("_")[0];
        const status = $('#'+name+'_status').html();
        const role = $('#'+name+'_role').html();
        socket.emit('detect check', {target: name});
        addWatcherMessage('Detect Event', 'Detective wants to check ' + name, socket);
    });

    $(document).on("click", "a[name='hang']", function(){
        const name = $(this).attr('id').split("_")[0];
        const status = $('#'+name+'_status').html();
        socket.emit('hang check', {target: name});
        if (status == 'Status: Alive') {
            socket.emit('hang', {target: name});
            $('a[name="hang"]').addClass('disabled');
            addMessage('Town Hall', name +' was executed by the townspeople', socket);
            socket.emit('disable hang');
        }
    });

    $('#observer').click(function() {
        $('#modal').modal('hide');
        socket.emit('observe');
    })

    $('#start').on('click', function() {       
        addMessage('Shuffling Roles', 'Randomly assign everyone a role', socket);
        socket.emit('shuffle');
        addMessage('Start', 'Game started! The hunt begins..', socket);
        socket.emit('disable start');
        nightProgression(socket);
    });

    $('#night').click(function() {
        addMessage('A Night Begins!', 'Everyone goes to sleep..', socket);
        nightProgression(socket);
    });

    $('#end').on('click', function(){
        addMessage('Game Over', 'The game has ended', socket);
        sessionStorage.clear();
        socket.emit('clear');
    });
});

$(window).on("unload", function(){
    sessionStorage.clear();
});