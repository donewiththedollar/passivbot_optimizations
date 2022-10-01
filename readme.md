# Passivbot Configurations
## Updates
  * **IMPORTANT NOTE FOR PARTICLE SWARM**
   * If you are using the particle swarm configurations you must use the latest version of passivbot ``git clone https://github.com/enarjord/passivbot.git``. I recommend a clean install. 
   
  * **10/01/22** - Live results with 0.1.4 have proven to produce profits during the bear market, with better gains with more upside as typically long exposures are higher than short exposures. Remember, longs your downside risk is to zero; while with shorts your downside risk is getting rekt to death infinitely as number can always go up. Due to good results with 0.1.4 and can be called safe, I have now optimized 0.1.4 using particle swarm optimization.
  
  * **9/6/22** - Have had success with particle swarm, will proceed with more PSOs to push limitations for higher ADGs, and then go from there for longer term passive. Although, these could be used passively as they use autounstuck. Only live results tell the full story even with proper backtest, although metrics on backtest do indeed align with what we see on live result. 
  
  * Currently optimizing with 1s tick on single asset in bulk batches. Backtest is in 1s tick as well.
#### Current configs of interest
##### 1m
  * https://github.com/donewiththedollar/passivbot_v5.7.1/tree/main/configs/PBSO/1m/0.1.2_auenabled_longshort
  * https://github.com/donewiththedollar/passivbot_v5.7.1/tree/main/configs/PBSO/1m/mdcl_hardcore_scalp
##### 1s tick
  * https://github.com/donewiththedollar/passivbot_v5.7.1/tree/main/configs/PBSO/1s/0.1.2_1sdata_auenabled_longshort
  * https://github.com/donewiththedollar/passivbot_v5.7.1/tree/main/configs/PBSO/1s/0.1.4_40%25grid_1sdata_auenabled_longshort
##### Particle swarm (**UPDATED 10/01/22**)
  * (**NEW**)https://github.com/donewiththedollar/passivbot_v5.8.0/tree/main/configs/PBSO/particle_swarm/PSO_0.1.4_reoptimized_new
  * https://github.com/donewiththedollar/passivbot_v5.7.1/tree/main/configs/PBSO/particle_swarm
  
### Community Repos
  * https://github.com/tedyptedto/pbos
  * https://github.com/JohnKearney1/PassivBot-Configurations
  

Proper risk management is key. Keep your wallet exposures low!

Also thanks to enarjord for this amazing project!

To install Passivbot, head over to https://github.com/enarjord/passivbot/

You must be using v5.7.1 or above to use most configurations posted here.

Also if you are using my configurations, please give feedback on discord in Passivbot Discord server or my Discord flyingtoaster#3285
