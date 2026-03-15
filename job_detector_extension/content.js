function markFakeJobs(){

    let jobs = document.querySelectorAll("h2, h3");

    jobs.forEach(job => {

        let text = job.innerText.toLowerCase();

        if(
            text.includes("earn money") ||
            text.includes("data entry") ||
            text.includes("work from home") ||
            text.includes("typing job")
        ){

            let warning = document.createElement("span");

            warning.innerText = " ⚠ Possible Fake Job";

            warning.style.color = "red";
            warning.style.fontWeight = "bold";

            job.appendChild(warning);
        }

    });

}

setTimeout(markFakeJobs, 3000);