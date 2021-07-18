function isSeller(id) {
    return  id.startsWith("seller");
}

function buildMsg() {
    var projects = document.getElementsByClassName("project");
    msg = {bidders: []};
    for (var j = 0; j < projects.length; j++) {
        var q = Number(projects[j].getElementsByClassName("quantity")[0].innerText);
        const input = projects[j].getElementsByTagName("input")[0];
        const id = projects[j].id;
        p = Number(input.value);
        if (p > 0 & q > 0) {
            if (isSeller(id)) {
                p = -p;
            } else {
                q = -q;
            }
            bidder = {"name": id, "bids": [{v: p, q: {P: q}}]};
            msg.bidders.push(bidder);
        }

    }
    return msg;
}

function displayOutcome(result) {

    const fmt = new Intl.NumberFormat('en-EN', {style: 'currency', currency: 'GBP'});

    const summary = document.getElementById("summary");
    const surplus = fmt.format(result.surplus);
    const nWinners = Object.keys(result.payments).length;
    document.getElementById("summaryText").innerHTML = `${nWinners} winning bidders, total surplus is ${surplus}`;


    var outcomes = document.getElementsByClassName("outcome");
    var id2outcome = {};
    for (var j = 0; j < outcomes.length; j++) {
        const id = outcomes[j].dataset.bid;
        id2outcome[id] = outcomes[j];
    }

    showSolution(true);

    result.problem.bidders.forEach(function (bidder, index) {
        const id = bidder.name;
        const winning = result.payments.hasOwnProperty(id);
        const element = id2outcome[id];
        if (winning) {
            const bonus = fmt.format(result.surplus_shares[id]);

            if (isSeller(id)) {
                const payment = fmt.format(-result.payments[id]);
                const bid = fmt.format(-result.payments[id] - result.surplus_shares[id]);
                element.innerHTML = `Winning, receives<br> ${bid} bid <br> + ${bonus} bonus <br> = ${payment}`;
            } else {
                const payment = fmt.format(result.payments[id]);
                const bid = fmt.format(result.payments[id] + result.surplus_shares[id]);
                element.innerHTML = `Winning, pays<br>  ${bid} bid <br> - ${bonus} discount <br> = ${payment}`;
            }

        } else {
            element.innerHTML = "Did not win";
        }
        delete id2outcome[id];
    });

    for (var key in id2outcome) {
        if (id2outcome.hasOwnProperty(key)) {
            id2outcome[key].innerHTML = "Did not bid";
        }
    }

}

function solveMarket() {

    const msg = buildMsg();
    var xmlhttp = new XMLHttpRequest();
    var theUrl = "/solve/lindsay2018";
    xmlhttp.open("POST", theUrl);
    xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    xmlhttp.onload = function () {
        if (xmlhttp.readyState === xmlhttp.DONE) {
            if (xmlhttp.status === 200) {
                var result = JSON.parse(xmlhttp.response);
                displayOutcome(result);
            }
            if (xmlhttp.status === 400) {
                console.log(xmlhttp.response);
            }
        }
    };

    xmlhttp.send(JSON.stringify(msg));
}

function reset() {
    showSolution(false);
}

function showSolution(showSolution) {
    var solDisplay = showSolution ? "block" : "none";
    var bidDisplay = showSolution ? "none" : "block";

    document.getElementById("solveMarket").style.display = bidDisplay;
    document.getElementById("summary").style.display = solDisplay;

    var outcomes = document.getElementsByClassName("outcome");
    for (var j = 0; j < outcomes.length; j++) {
        outcomes[j].style.display = solDisplay;
    }

    var inputs = document.getElementsByTagName("input");
    for (var j = 0; j < inputs.length; j++) {
        inputs[j].disabled = showSolution;
    }
}


