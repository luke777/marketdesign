function isSeller(id) {
    return  id.startsWith("seller");
}

function buildMsg() {
    const projects = document.getElementsByClassName("project");
    const msg = {bidders: []};

    for (let j = 0; j < projects.length; j++) {
        let q = Number(projects[j].getElementsByClassName("quantity")[0].innerText);
        const input = projects[j].getElementsByTagName("input")[0];
        const id = projects[j].id;
        let p = Number(input.value);
        if (p > 0 && q > 0) {
            if (isSeller(id)) {
                p = -p;
            } else {
                q = -q;
            }
            let bidder = {"name": id, "bids": [{v: p, q: {P: q}}]};
            msg.bidders.push(bidder);
        }

    }
    return msg;
}

function displayOutcome(result) {

    const fmt = new Intl.NumberFormat('en-EN', {style: 'currency', currency: 'GBP'});

    const surplus = fmt.format(result.surplus);
    const nWinners = Object.keys(result.payments).length;
    document.getElementById("summaryText").innerHTML = `${nWinners} winning bidders, total surplus is ${surplus}`;


    const outcomes = document.getElementsByClassName("outcome");
    const id2outcome = {};
    for (let j = 0; j < outcomes.length; j++) {
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

    for (let key in id2outcome) {
        if (id2outcome.hasOwnProperty(key)) {
            id2outcome[key].innerHTML = "Did not bid";
        }
    }

}

function solveMarket() {

    const msg = buildMsg();
    const xmlHttp = new XMLHttpRequest();
    const url = "/solve/lindsay2018";
    xmlHttp.open("POST", url);
    xmlHttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    xmlHttp.onload = function () {
        if (xmlHttp.readyState === xmlHttp.DONE) {
            if (xmlHttp.status === 200) {
                var result = JSON.parse(xmlHttp.response);
                displayOutcome(result);
            }
            if (xmlHttp.status === 400) {
                console.log(xmlHttp.response);
            }
        }
    };

    xmlHttp.send(JSON.stringify(msg));
}

function reset() {
    showSolution(false);
}

function showSolution(showSolution) {
    const solDisplay = showSolution ? "block" : "none";
    document.getElementById("solveMarket").style.display = showSolution ? "none" : "block";
    document.getElementById("summary").style.display = solDisplay;

    const outcomes = document.getElementsByClassName("outcome");
    for (let j = 0; j < outcomes.length; j++) {
        outcomes[j].style.display = solDisplay;
    }

    const inputs = document.getElementsByTagName("input");
    for (let j = 0; j < inputs.length; j++) {
        inputs[j].disabled = showSolution;
    }
}


