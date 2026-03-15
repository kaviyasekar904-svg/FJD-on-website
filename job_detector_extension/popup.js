document.getElementById("scan").addEventListener("click", async () => {

    let [tab] = await chrome.tabs.query({active: true, currentWindow: true});

    chrome.scripting.executeScript({
        target: {tabId: tab.id},
        func: sendJobsToAI
    });

});

function sendJobsToAI(){

    let jobs = [];

    function getJobUrl(el){
        if (!el) return "";
        let link = el.closest("a[href]");
        if (link && link.href) return link.href;
        link = el.querySelector("a[href]");
        if (link && link.href) return link.href;
        let parent = el.parentElement;
        let depth = 0;
        while (parent && depth < 4){
            link = parent.querySelector("a[href]");
            if (link && link.href) return link.href;
            parent = parent.parentElement;
            depth += 1;
        }
        return "";
    }

    function getCompanyForTitle(titleEl){
        if (!titleEl) return "";
        const dataCompany = titleEl.getAttribute("data-company");
        if (dataCompany) return dataCompany.trim();
        const container = titleEl.closest("article, li, tr, div, section") || titleEl.parentElement;
        if (container){
            const containerCompany = container.getAttribute("data-company");
            if (containerCompany) return containerCompany.trim();
            const companyEl = container.querySelector("h3");
            if (companyEl && companyEl.innerText.trim()) return companyEl.innerText.trim();
        }
        const parent = titleEl.parentElement;
        if (parent){
            const siblingCompany = parent.querySelector("h3");
            if (siblingCompany && siblingCompany.innerText.trim()) return siblingCompany.innerText.trim();
        }
        return "";
    }

    document.querySelectorAll("h2").forEach((job)=>{
        let title = job.innerText.trim();
        let company = getCompanyForTitle(job);
        let url = getJobUrl(job);
        if (title){
            jobs.push(title + "||" + company + "||" + url);
        }
    });

    let job_text = jobs.join("|");

    let url = "http://localhost:8501/?jobs=" + encodeURIComponent(job_text);

    window.open(url);
}
