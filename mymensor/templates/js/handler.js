{% loadbinstant_tags %}

function handlers_for_event(event_class, channel, message, data, site, uid) {
    if (( event_class == 'NewMedia' ) && ("{{user.get_username}}" == JSON.stringify(data.username).replace(/\"/g, ""))) {
        console.log("NewMedia");
        console.log("Event Class:" + event_class);
        console.log("Channel:" + channel);
        console.log("Message:" + message);
        console.log("Data:" + data);
        console.log("Site:" + site);
        console.log("Uid:" + uid);
    }

}




