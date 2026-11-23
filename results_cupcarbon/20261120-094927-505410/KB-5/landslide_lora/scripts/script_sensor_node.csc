// ==============================================================

// SENSCRIPT FOR SENSOR NODES (Node 1 -> Node 10)

// Kich ban mo phong V2: Giam sat sat lo dat LoRa P2P tren CupCarbon

// Co che: Blind Replication (Khong ACK) + Deduplication + Silence Bypass

// ==============================================================



atget id myid



// 1. CHON KICH BAN MO PHONG (0: KB-0, 1: KB-1, 2: KB-2, 3: KB-3, 4: KB-4, 5: KB-5, 6: KB-6)

set SCENARIO 5



// 2. THIET LAP HANG SO MAC DINH THEO KICH BAN

set W_RAIN 0

set T_RAIN_START 9999

set T_RAIN_END 9999

set LS_TYPE 0

set T_LS 73

set FAIL_NODE 0

set T_FAIL 9999



if (SCENARIO == 0)

  set W_RAIN 0

  set T_RAIN_START 9999

  set LS_TYPE 0

  set FAIL_NODE 0

  set T_FAIL 9999

endif



if (SCENARIO == 1)

  set W_RAIN 12

  set T_RAIN_START 26

  set T_RAIN_END 200

  set LS_TYPE 0

  set FAIL_NODE 0

  set T_FAIL 9999

endif



if (SCENARIO == 2)

  set W_RAIN 25

  set T_RAIN_START 26

  set T_RAIN_END 200

  set LS_TYPE 0

  set FAIL_NODE 0

  set T_FAIL 9999

endif



if (SCENARIO == 3)

  set W_RAIN 12

  set T_RAIN_START 26

  set T_RAIN_END 9999

  set LS_TYPE 1

  set T_LS 73

  set FAIL_NODE 0

  set T_FAIL 9999

endif



if (SCENARIO == 4)

  set W_RAIN 12

  set T_RAIN_START 26

  set T_RAIN_END 9999

  set LS_TYPE 2

  set T_LS 73

  set FAIL_NODE 0

  set T_FAIL 9999

endif



if (SCENARIO == 5)

  set W_RAIN 0

  set T_RAIN_START 9999

  set LS_TYPE 0

  set FAIL_NODE 3

  set T_FAIL 90

endif



if (SCENARIO == 6)

  set W_RAIN 12

  set T_RAIN_START 26

  set T_RAIN_END 9999

  set LS_TYPE 2

  set T_LS 73

  set FAIL_NODE 5

  set T_FAIL 93

endif



// 3. CAU HINH THAM SO MANG VA CAM BIEN

set BASE_VAL 20

set THETA 5

set RAIN_JUMP 22

set curval 20

set prevval 20

set seq 0



// So ban sao phat lap (Replication)

set REP_F0 1

set REP_F100 2

set REP_F255 3

set REP_F150 3

set REP_F200 3

set JIT_MIN 100

set JIT_MAX 400



// Nghe im lang (Silence detection) - Tinh chinh theo Diem 2

set M_MISS 3

set T_SIL_MIN 70

set T_SIL_MAX 90



// 4. TOPOLOGY VA DINH TUYEN TAI CHO

if (myid == 1)

  set nexthop 11

else

  minus nexthop myid 1

  int nexthop nexthop

endif



if (myid == 10)

  set child 0

else

  plus child myid 1

  int child child

endif



set bypass_next 0

set bypass_child 0

set bypass_child_id 0



// Bien trang thai

set lvl 0

set sleepms 5000

set stablecnt 0

set escalate_timer 0

set lastheard 0

set tnow 0



// Bang khu trung lap theo SRC (1..10)

set ls1 0

set ls2 0

set ls3 0

set ls4 0

set ls5 0

set ls6 0

set ls7 0

set ls8 0

set ls9 0

set ls10 0



mark 1

led 1 0



time tnow

cprint "[INIT] Sensor Node " myid " khoi dong. NextHop: " nexthop " Child: " child



loop

  time tnow



  // 1. KIEM TRA HONG CUNG (FAIL_NODE)

  if (myid == FAIL_NODE)

    if (tnow >= T_FAIL)

      cprint "[FAIL] t=" tnow " node=" myid

      mark 0

      led 1 0

      stop

    endif

  endif



  // Fast-Failover: Sender chu dong bo qua nut ke bi hong

  if (0 == 1)

    if (nexthop == FAIL_NODE)

      if (tnow >= T_FAIL)

        if (bypass_next == 0)

          set bypass_next 1

          if (nexthop == 1)

            set nexthop 11

          else

            minus nexthop nexthop 1

            int nexthop nexthop

          endif

          cprint "[BYPASS_ON] t=" tnow " node=" myid " next=" nexthop

        endif

      endif

    endif

  endif



  // 2. GIA LAP CAM BIEN VA XAC DINH SU KIEN

  set is_raining 0

  if (tnow >= T_RAIN_START)

    if (tnow <= T_RAIN_END)

      set is_raining 1

    endif

  endif



  randb noise -2 2

  plus curval BASE_VAL noise



  if (is_raining == 1)

    if (myid >= 4)

      if (myid <= 7)

        plus curval curval RAIN_JUMP

      endif

    endif

  endif



  if (LS_TYPE > 0)

    if (myid == 5)

      if (tnow >= T_LS)

        randb ls_noise 0 4

        plus curval 88 ls_noise

      endif

    endif

  endif



  dreadsensor evt

  if (evt == 1)

    set curval 92

  endif



  minus dval curval prevval

  if (dval < 0)

    minus delta 0 dval

  else

    set delta dval

  endif

  set prevval curval



  set myflag 0

  set myval delta

  if (curval >= 85)

    set myflag 255

    set myval curval

  else

    if (curval >= 40)

      set myflag 100

      set myval curval

    endif

  endif



  // 3. DIEU KHIEN CHU KY NGU THICH UNG VA LED

  if (myflag == 255)

    set lvl 0

    set stablecnt 0

    mark 1

    led 1 0

  else

    if (tnow < escalate_timer)

      set lvl 0

      mark 1

      led 1 0

    else

      if (myflag == 100)

        set lvl 1

        set stablecnt 0

        mark 0

        led 1 4

      else

        if (delta >= THETA)

          set lvl 0

          set stablecnt 0

          mark 1

          led 1 0

        else

          plus stablecnt stablecnt 1

          if (stablecnt >= 6)

            set lvl 2

            mark 0

            led 1 2

          else

            if (stablecnt >= 3)

              set lvl 1

              mark 0

              led 1 4

            else

              set lvl 0

              mark 1

              led 1 0

            endif

          endif

        endif

      endif

    endif

  endif



  if (lvl == 0)

    set sleepms 5000

  endif

  if (lvl == 1)

    set sleepms 15000

  endif

  if (lvl == 2)

    set sleepms 30000

  endif



  // 4. TAO GOI TIN GOC CUA CHINH NUT VA PHAT LAP

  plus seq seq 1

  time tnow

  cprint "[GEN] t=" tnow " node=" myid " src=" myid " seq=" seq " flag=" myflag " val=" myval



  set num_copies REP_F0

  if (myflag == 255)

    set num_copies REP_F255

  endif

  if (myflag == 100)

    set num_copies REP_F100

  endif

  if (myflag == 0)

    if (is_raining == 1)

      set num_copies 2

    endif

  endif



  set c 0

  while (c < num_copies)

    plus c c 1

    time tnow

    data pkt myid myflag myval seq myid tnow tnow

    cprint "[TX] t=" tnow " node=" myid " to=" nexthop " src=" myid " seq=" seq " flag=" myflag " copy=" c "/" num_copies " bypass=" bypass_next

    send pkt nexthop

    if (c < num_copies)

      randb jit JIT_MIN JIT_MAX

      delay jit

    endif

  endwhile



  randb txgap 150 250

  delay txgap



  // 5. CUA SO XU LY HANG DOI NHAN

  buffer b

  time tnow

  cprint "[BUF] t=" tnow " node=" myid " b=" b

  while (b >= 0)

    read rxpkt

    rdata rxpkt rsrc rflag rval rseq rprev rtgen rttx



    // (a) Loc lang gieng logic

    minus hdist rprev myid

    if (hdist < 0)

      minus absgap 0 hdist

    else

      set absgap hdist

    endif



    set pkt_ok 0

    if (absgap == 1)

      set pkt_ok 1

    endif

    if (absgap == 2)

      if (rflag == 200)

        set pkt_ok 1

      endif

      if (bypass_child == 1)

        if (rprev == bypass_child_id)

          set pkt_ok 1

        endif

      endif

      if (bypass_next == 1)

        if (rprev == nexthop)

          set pkt_ok 1

        endif

      endif

      if (child > 0)

        plus next_child child 1

        int next_child next_child

        if (rprev == next_child)

          set pkt_ok 1

          set bypass_child 1

          set bypass_child_id next_child

        endif

      endif

    endif



    if (pkt_ok == 0)

      time tnow

      cprint "[IGNORE] t=" tnow " rx=" myid " from=" rprev " src=" rsrc " seq=" rseq

    else

      // (b) Mo hinh kenh truyen & Mat goi

      set p_drop 0

      set drop_cause "NONE"



      if (is_raining == 1)

        set p_drop W_RAIN

        set drop_cause "RAIN"

      endif



      set in_ls 0

      if (myid >= 4)

        if (myid <= 7)

          set in_ls 1

        endif

      endif

      if (rprev >= 4)

        if (rprev <= 7)

          set in_ls 1

        endif

      endif



      if (LS_TYPE > 0)

        if (tnow >= T_LS)

          if (in_ls == 1)

            if (LS_TYPE == 1)

              randb r_ls 40 50

              minus t_gap tnow T_LS

              div f_ramp t_gap 60

              if (f_ramp > 1)

                set f_ramp 1

              endif

              mult p_ls r_ls f_ramp

              int p_ls p_ls

              if (p_ls > p_drop)

                set p_drop p_ls

                set drop_cause "LANDSLIDE"

              endif

            endif

            if (LS_TYPE == 2)

              randb r_ls 80 85

              if (r_ls > p_drop)

                set p_drop r_ls

                set drop_cause "LANDSLIDE"

              endif

            endif

          endif

        endif

      endif



      if (absgap == 2)

        plus p_drop p_drop 10

        if (p_drop > 95)

          set p_drop 95

        endif

        set drop_cause "BYPASS"

      endif



      randb roll 1 100

      if (roll <= p_drop)

        time tnow

        cprint "[DROP] t=" tnow " rx=" myid " from=" rprev " src=" rsrc " seq=" rseq " flag=" rflag " p=" p_drop " cause=" drop_cause

      else

        // (c) Nhan goi tin thanh cong

        time tnow

        cprint "[RX] t=" tnow " rx=" myid " from=" rprev " src=" rsrc " seq=" rseq " flag=" rflag



        // (d) Giam sat nut ke & Hoan tac (REVERT)

        if (rprev == child)

          set lastheard tnow

          if (bypass_child == 1)

            set bypass_child 0

            time tnow

            cprint "[REVERT] t=" tnow " node=" myid " child=" child

            if (child < 10)

              plus seq seq 1

              data revpkt myid 200 0 seq myid tnow tnow

              send revpkt bypass_child_id

            endif

          endif

        endif



        if (bypass_child == 1)

          if (rprev == bypass_child_id)

            set lastheard tnow

            time tnow

            cprint "[CONFIRM] t=" tnow " node=" myid " from=" rprev

          endif

        endif



        // (e) Khu trung lap theo SRC

        set is_dup 0

        if (rsrc == 1)

          if (rseq <= ls1)

            set is_dup 1

          else

            set ls1 rseq

          endif

        endif

        if (rsrc == 2)

          if (rseq <= ls2)

            set is_dup 1

          else

            set ls2 rseq

          endif

        endif

        if (rsrc == 3)

          if (rseq <= ls3)

            set is_dup 1

          else

            set ls3 rseq

          endif

        endif

        if (rsrc == 4)

          if (rseq <= ls4)

            set is_dup 1

          else

            set ls4 rseq

          endif

        endif

        if (rsrc == 5)

          if (rseq <= ls5)

            set is_dup 1

          else

            set ls5 rseq

          endif

        endif

        if (rsrc == 6)

          if (rseq <= ls6)

            set is_dup 1

          else

            set ls6 rseq

          endif

        endif

        if (rsrc == 7)

          if (rseq <= ls7)

            set is_dup 1

          else

            set ls7 rseq

          endif

        endif

        if (rsrc == 8)

          if (rseq <= ls8)

            set is_dup 1

          else

            set ls8 rseq

          endif

        endif

        if (rsrc == 9)

          if (rseq <= ls9)

            set is_dup 1

          else

            set ls9 rseq

          endif

        endif

        if (rsrc == 10)

          if (rseq <= ls10)

            set is_dup 1

          else

            set ls10 rseq

          endif

        endif



        if (is_dup == 1)

          time tnow

          cprint "[DUP] t=" tnow " rx=" myid " src=" rsrc " seq=" rseq

        else

          // (f) Xu ly goi REPAIR (FLAG 200)

          if (rflag == 200)

            time tnow

            if (rval == 0)

              set bypass_next 0

              if (myid == 1)

                set nexthop 11

              else

                minus nexthop myid 1

  int nexthop nexthop

              endif

              cprint "[REVERT] t=" tnow " node=" myid " next=" nexthop

            else

              set bypass_next 1

              set nexthop rprev

              int nexthop nexthop

              cprint "[BYPASS_ON] t=" tnow " node=" myid " next=" nexthop

            endif

          else

            // (g) Leo thang bao dong xuoi dong

            if (rflag == 255)

              set lvl 0

              plus escalate_timer tnow 60

              mark 1

              led 1 0

            endif

            if (rflag == 150)

              set lvl 0

              plus escalate_timer tnow 60

              mark 1

              led 1 4

            endif



            // (h) Chuyen tiep ban dau tien (FWD)

            time tnow

            cprint "[FWD] t=" tnow " node=" myid " src=" rsrc " seq=" rseq



            set fwd_rep 1

            if (rflag == 255)

              set fwd_rep REP_F255

            endif

            if (rflag == 150)

              set fwd_rep REP_F150

            endif

            if (rflag == 100)

              set fwd_rep REP_F100

            endif



            set fc 0

            while (fc < fwd_rep)

              plus fc fc 1

              time tnow

              data fwdpkt rsrc rflag rval rseq myid rtgen tnow

              cprint "[TX] t=" tnow " node=" myid " to=" nexthop " src=" rsrc " seq=" rseq " flag=" rflag " copy=" fc "/" fwd_rep " bypass=" bypass_next

              send fwdpkt nexthop

              if (fc < fwd_rep)

                randb fjit JIT_MIN JIT_MAX

                delay fjit

              endif

            endwhile



            randb fwdgap 150 250

            delay fwdgap

          endif

        endif

      endif

    endif



    buffer b

  endwhile



  // 6. GIAM SAT IM LANG VA KICH HOAT NOI VONG

  if (child > 0)

    if (bypass_child == 0)

      time tnow

      minus sil_elapsed tnow lastheard

      div s_sec sleepms 1000

      mult c_sil M_MISS s_sec

      int c_sil c_sil



      set t_sil c_sil

      if (t_sil < T_SIL_MIN)

        set t_sil T_SIL_MIN

      endif

      if (t_sil > T_SIL_MAX)

        set t_sil T_SIL_MAX

      endif



      if (sil_elapsed >= t_sil)

        cprint "[DETECT] t=" tnow " node=" myid " child=" child



        // Leo thang chu ky de tiep nhan noi vong nhanh chong

        set lvl 0

        set sleepms 5000

        plus escalate_timer tnow 60

        mark 1

        led 1 4



        // Phat bao dong mat nut (FLAG 150)

        plus seq seq 1

        time tnow

        cprint "[GEN] t=" tnow " node=" myid " src=" myid " seq=" seq " flag=150 val=" child

        set c 0

        while (c < REP_F150)

          plus c c 1

          time tnow

          data lostpkt myid 150 child seq myid tnow tnow

          cprint "[TX] t=" tnow " node=" myid " to=" nexthop " src=" myid " seq=" seq " flag=150 copy=" c "/" REP_F150 " bypass=" bypass_next

          send lostpkt nexthop

          if (c < REP_F150)

            randb jit JIT_MIN JIT_MAX

            delay jit

          endif

        endwhile



        randb txgap 200 300

        delay txgap



        set bypass_child 1

        set lastheard tnow

        // Kich hoat noi vong neu chua toi nut cuoi (child < 10)

        if (child < 10)

          plus bypass_child_id child 1

          int bypass_child_id bypass_child_id



          cprint "[REPAIR_TX] t=" tnow " node=" myid " to=" bypass_child_id " failed=" child

          set rc 0

          plus seq seq 1

          while (rc < REP_F200)

            plus rc rc 1

            time tnow

            data repairpkt myid 200 child seq myid tnow tnow

            send repairpkt bypass_child_id

            randb rjit 200 350

            delay rjit

          endwhile

        endif

      endif

    endif

  endif



  // 7. NGU THEO CHU KY THICH UNG

  delay sleepms

