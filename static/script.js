const form=document.getElementById("searchForm"),input=document.getElementById("cityInput"),statusEl=document.getElementById("status"),weatherEl=document.getElementById("weather");
function dayName(date){return new Date(date+"T12:00:00").toLocaleDateString(undefined,{weekday:"short"})}
function render(data){
document.getElementById("location").textContent=data.location;document.getElementById("updated").textContent="Updated: "+data.updated.replace("T"," ");
document.getElementById("icon").textContent=data.current.icon;document.getElementById("temp").textContent=data.current.temperature;document.getElementById("description").textContent=data.current.description;
document.getElementById("feels").textContent=data.current.feels_like+"°C";document.getElementById("humidity").textContent=data.current.humidity+"%";document.getElementById("wind").textContent=data.current.wind+" km/h";
document.getElementById("forecast").innerHTML=data.forecast.map(x=>'<article class="forecast-card"><div class="day">'+dayName(x.date)+'</div><div class="ficon">'+x.icon+'</div><div class="range">'+x.max+'° / '+x.min+'°</div><div class="rain">💧 '+x.rain+'% rain</div></article>').join("");
weatherEl.classList.remove("hidden")}
async function searchWeather(city){statusEl.textContent="Loading live weather...";try{const r=await fetch("/api/weather?city="+encodeURIComponent(city)),d=await r.json();if(!r.ok)throw new Error(d.error||"Unable to load weather.");render(d);statusEl.textContent=""}catch(e){weatherEl.classList.add("hidden");statusEl.textContent=e.message}}
form.addEventListener("submit",e=>{e.preventDefault();const city=input.value.trim();if(city)searchWeather(city)});searchWeather("Hyderabad");
