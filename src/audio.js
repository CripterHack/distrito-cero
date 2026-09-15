'use strict';
(function(D){
 class Audio{
  constructor(){this.ctx=null;this.enabled=true;this.music=false;this.lastBeat=-1;this.lastStep=0;this.volume=.5;}
  async start(){
   if(!this.ctx){
    const AC=globalThis.AudioContext||globalThis.webkitAudioContext;if(!AC)return;
    this.ctx=new AC();const c=this.ctx;this.master=c.createGain();this.master.gain.value=this.enabled?this.volume:0;this.master.connect(c.destination);
    this.engine=c.createOscillator();this.engine.type='sawtooth';this.engine.frequency.value=38;this.engineFilter=c.createBiquadFilter();this.engineFilter.type='lowpass';this.engineFilter.frequency.value=160;this.engineGain=c.createGain();this.engineGain.gain.value=0;this.engine.connect(this.engineFilter);this.engineFilter.connect(this.engineGain);this.engineGain.connect(this.master);this.engine.start();
    this.siren=c.createOscillator();this.siren.type='sine';this.siren.frequency.value=580;this.sirenGain=c.createGain();this.sirenGain.gain.value=0;this.siren.connect(this.sirenGain);this.sirenGain.connect(this.master);this.siren.start();
    const buffer=c.createBuffer(1,c.sampleRate*3,c.sampleRate),data=buffer.getChannelData(0);let last=0;for(let i=0;i<data.length;i++){last=(last+(Math.random()*2-1)*.05)/1.05;data[i]=last*3.5;}this.noiseBuffer=buffer;
    this.rain=c.createBufferSource();this.rain.buffer=buffer;this.rain.loop=true;this.rainGain=c.createGain();this.rainGain.gain.value=.1;this.rain.connect(this.rainGain);this.rainGain.connect(this.master);this.rain.start();
   }
   if(this.ctx.state==='suspended')try{await this.ctx.resume();}catch(e){/* The sound button lets the player retry. */}
  }
  mute(muted){this.enabled=!muted;if(this.ctx)this.master.gain.setTargetAtTime(this.enabled?this.volume:0,this.ctx.currentTime,.08);}
  setVolume(value){this.volume=D.clamp(value,0,1);this.mute(!this.enabled);}
  tone(freq,duration=.12,gain=.06,type='sine',end){if(!this.ctx)return;let c=this.ctx,o=c.createOscillator(),g=c.createGain();o.type=type;o.frequency.value=freq;if(end)o.frequency.exponentialRampToValueAtTime(end,c.currentTime+duration);g.gain.setValueAtTime(gain,c.currentTime);g.gain.exponentialRampToValueAtTime(.001,c.currentTime+duration);o.connect(g);g.connect(this.master);o.start();o.stop(c.currentTime+duration+.02);}
  effect(name){
   if(!this.ctx||!this.enabled)return;
   if(name==='horn'){this.tone(196,.45,.12,'sawtooth');this.tone(246.94,.45,.1,'sawtooth');}
   if(name==='door')this.tone(100,.13,.15,'triangle',30);
   if(name==='reward'){this.tone(523,.2,.065,'sine');setTimeout(()=>this.tone(784,.3,.06,'sine'),95);}
   if(name==='crash'){const c=this.ctx,s=c.createBufferSource(),g=c.createGain();s.buffer=this.noiseBuffer;g.gain.setValueAtTime(.6,c.currentTime);g.gain.exponentialRampToValueAtTime(.001,c.currentTime+.32);s.connect(g);g.connect(this.master);s.start();s.stop(c.currentTime+.33);this.tone(68,.22,.27,'triangle',25);}
  }
  update(sim,paused,rain){
   if(!this.ctx)return;const c=this.ctx,t=c.currentTime,car=sim.player.car!==null?sim.actor():null,speed=car?Math.abs(car.speed):0;
   this.engine.frequency.setTargetAtTime(34+speed*3.7,t,.12);this.engineFilter.frequency.setTargetAtTime(160+speed*17,t,.12);this.engineGain.gain.setTargetAtTime(car&&!paused?.055+speed*.001:0,t,.1);
   let nearest=Infinity;for(let v of sim.cars)if(v.police&&!v.stolen&&v!==sim.actor())nearest=Math.min(nearest,D.distance(v,sim.player));
   this.siren.frequency.setTargetAtTime(620+Math.sin(sim.time*4.5)*190,t,.06);this.sirenGain.gain.setTargetAtTime(sim.wanted&&!paused?Math.max(0,1-nearest/100)*.035:0,t,.1);this.rainGain.gain.setTargetAtTime(paused?.025:.07*rain,t,.15);
   if(!paused&&!car&&sim.player.moving&&sim.time-this.lastStep>.34){this.lastStep=sim.time;this.tone(65,.04,.055,'triangle',30);}
   let beat=Math.floor(sim.time*2.4);if(this.music&&!paused&&beat!==this.lastBeat){this.lastBeat=beat;const notes=[130.81,155.56,196,233.08,196,155.56,116.54,155.56];this.tone(notes[beat%8],.35,.017,'triangle');if(beat%4===0)this.tone(43.65,.6,.05,'sine');}
  }
 }
 D.Audio=Audio;
})(DC);
