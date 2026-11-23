// ==============================================================

// SENSCRIPT FOR GATEWAY SINK (Node 11)

// Kich ban mo phong V2: Giam sat sat lo dat LoRa P2P tren CupCarbon

// Nhiem vu: Thu thap du lieu, do tre lat=tnow-tgen, khu trung lap,

//           giam sat nut S1, va xuat log chuan theo Muc 7.

// ==============================================================



atget id myid

mark 1

led 1 1



// 1. CAU HINH KICH BAN (DONG BO VOI SENSOR NODES)

set SCENARIO 0



set W_RAIN 0

set T_RAIN_START 9999

set T_RAIN_END 9999



if (SCENARIO == 1)

  set W_RAIN 12

  set T_RAIN_START 26

  set T_RAIN_END 200

endif

if (SCENARIO == 2)

  set W_RAIN 25

  set T_RAIN_START 26

  set T_RAIN_END 200

endif

if (SCENARIO == 3)

  set W_RAIN 12

  set T_RAIN_START 26

  set T_RAIN_END 9999

endif

if (SCENARIO == 4)

  set W_RAIN 12

  set T_RAIN_START 26

  set T_RAIN_END 9999

endif

if (SCENARIO == 6)

  set W_RAIN 12

  set T_RAIN_START 26

  set T_RAIN_END 9999

endif



// 2. KHOI TAO TRANG THAI VA BO DEM THONG KE

set child 1

set bypass_child 0

set bypass_child_id 2

set lastheard 0

set repair_seq 0

set tnow 0

set summary_printed 0



// Khang dinh thoi gian im lang cua S1 (clamp 30s..90s)

set T_SIL 100



// Deduplication: luu SEQ lon nhat cua tung SRC

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



// Dem so goi duy nhat nhan duoc tu tung SRC

set cnt1 0

set cnt2 0

set cnt3 0

set cnt4 0

set cnt5 0

set cnt6 0

set cnt7 0

set cnt8 0

set cnt9 0

set cnt10 0



// Tong so goi theo co

set tot_f0 0

set tot_f100 0

set tot_f255 0

set tot_f150 0



cprint "=========================================================="

cprint ">>> GATEWAY TRUNG TAM (Sink Node " myid ") DA SAN SANG <<<"

cprint "=========================================================="



loop

  time tnow



  // 1. RUT CAN HANG DOI GOI TIN (BUFFER DRAIN - DIEM 3)

  buffer b

  while (b >= 0)

    read rxpkt

    rdata rxpkt rsrc rflag rval rseq rprev rtgen rttx



    // (a) Loc lang gieng logic cho Gateway

    set gw_ok 0

    if (rprev == 1)

      set gw_ok 1

    endif

    if (rprev == 2)

      set gw_ok 1

      set bypass_child 1

      set lastheard tnow

    endif



    if (gw_ok == 0)

      time tnow

      cprint "[IGNORE] t=" tnow " rx=" myid " from=" rprev " src=" rsrc " seq=" rseq

    else

      // (b) Mat goi tren chang cuoi ve Gateway (P_LINK)

      set is_rain 0

      if (tnow >= T_RAIN_START)

        if (tnow <= T_RAIN_END)

          set is_rain 1

        endif

      endif



      set p_drop 0

      set drop_cause "NONE"

      if (is_rain == 1)

        set p_drop W_RAIN

        set drop_cause "RAIN"

      endif



      if (rprev == 2)

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

        // (c) Ghi nhan ket noi song tu nut ket noi truc tiep

        if (rprev == child)

          set lastheard tnow

          if (bypass_child == 1)

            set bypass_child 0

            time tnow

            cprint "[REVERT] t=" tnow " node=" myid " child=" child

            plus repair_seq repair_seq 1

            data revpkt myid 200 0 repair_seq myid tnow tnow

            send revpkt 2

          endif

        endif



        if (bypass_child == 1)

          if (rprev == 2)

            set lastheard tnow

            time tnow

            cprint "[CONFIRM] t=" tnow " node=" myid " from=" rprev

          endif

        endif



        // (d) Khu trung lap theo (SRC, SEQ)

        set is_dup 0

        if (rsrc == 1)

          if (rseq <= ls1)

            set is_dup 1

          else

            set ls1 rseq

            plus cnt1 cnt1 1

          endif

        endif

        if (rsrc == 2)

          if (rseq <= ls2)

            set is_dup 1

          else

            set ls2 rseq

            plus cnt2 cnt2 1

          endif

        endif

        if (rsrc == 3)

          if (rseq <= ls3)

            set is_dup 1

          else

            set ls3 rseq

            plus cnt3 cnt3 1

          endif

        endif

        if (rsrc == 4)

          if (rseq <= ls4)

            set is_dup 1

          else

            set ls4 rseq

            plus cnt4 cnt4 1

          endif

        endif

        if (rsrc == 5)

          if (rseq <= ls5)

            set is_dup 1

          else

            set ls5 rseq

            plus cnt5 cnt5 1

          endif

        endif

        if (rsrc == 6)

          if (rseq <= ls6)

            set is_dup 1

          else

            set ls6 rseq

            plus cnt6 cnt6 1

          endif

        endif

        if (rsrc == 7)

          if (rseq <= ls7)

            set is_dup 1

          else

            set ls7 rseq

            plus cnt7 cnt7 1

          endif

        endif

        if (rsrc == 8)

          if (rseq <= ls8)

            set is_dup 1

          else

            set ls8 rseq

            plus cnt8 cnt8 1

          endif

        endif

        if (rsrc == 9)

          if (rseq <= ls9)

            set is_dup 1

          else

            set ls9 rseq

            plus cnt9 cnt9 1

          endif

        endif

        if (rsrc == 10)

          if (rseq <= ls10)

            set is_dup 1

          else

            set ls10 rseq

            plus cnt10 cnt10 1

          endif

        endif



        if (is_dup == 1)

          time tnow

          cprint "[DUP] t=" tnow " rx=" myid " src=" rsrc " seq=" rseq

        else

          // (e) Tinh do tre dau cuoi va xuat log [GW]

          time tnow

          minus lat tnow rtgen

          if (lat < 0)

            set lat 0.0

          endif

          cprint "[GW] t=" tnow " src=" rsrc " seq=" rseq " flag=" rflag " val=" rval " lat=" lat



          // Dem so luong theo co

          if (rflag == 255)

            plus tot_f255 tot_f255 1

            led 1 0

            cprint ">>> [GATEWAY - NGUY CAP] PHAT HIEN SAT LO DAT TAI NODE " rsrc " | Chi so: " rval " <<<"

          endif

          if (rflag == 150)

            plus tot_f150 tot_f150 1

            led 1 4

            cprint ">>> [GATEWAY - MAT NUT] NODE " rval " MAT LIEN LAC (bao boi NODE " rsrc ") <<<"

          endif

          if (rflag == 100)

            plus tot_f100 tot_f100 1

            led 1 4

            cprint ">>> [GATEWAY - CANH BAO] Phat hien MUA TO tai Node " rsrc " | Do am: " rval " <<<"

          endif

          if (rflag == 0)

            plus tot_f0 tot_f0 1

            led 1 1

            cprint "[GATEWAY] Nhan Delta tu Node " rsrc " | Do lech Delta: " rval

          endif

        endif

      endif

    endif



    buffer b

  endwhile



  // 2. GIAM SAT IM LANG NUT CON S1

  if (bypass_child == 0)

    time tnow

    minus sil_elapsed tnow lastheard

    if (sil_elapsed >= T_SIL)

      cprint "[DETECT] t=" tnow " node=" myid " child=1"

      cprint ">>> [GATEWAY - MAT NUT] NODE 1 MAT LIEN LAC <<<"

      set bypass_child 1

      set lastheard tnow

      plus repair_seq repair_seq 1

      cprint "[REPAIR_TX] t=" tnow " node=" myid " to=2 failed=1"

      set rgc 0

      while (rgc < 3)

        plus rgc rgc 1

        time tnow

        data rep_pkt myid 200 1 repair_seq myid tnow tnow

        send rep_pkt 2

        randb rgjit 200 350

        delay rgjit

      endwhile

    endif

  endif



  // 3. IN [SUMMARY] TAI CUOI PHIEN (t >= 395s)

  if (tnow >= 395)

    if (summary_printed == 0)

      set summary_printed 1

      cprint "[SUMMARY] t=" tnow " total_255=" tot_f255 " total_150=" tot_f150 " total_100=" tot_f100 " total_0=" tot_f0

      cprint "[SUMMARY_NODES] S1=" cnt1 "/" ls1 " S2=" cnt2 "/" ls2 " S3=" cnt3 "/" ls3 " S4=" cnt4 "/" ls4 " S5=" cnt5 "/" ls5 " S6=" cnt6 "/" ls6 " S7=" cnt7 "/" ls7 " S8=" cnt8 "/" ls8 " S9=" cnt9 "/" ls9 " S10=" cnt10 "/" ls10

    endif

  endif



  // Nghi nhip ngan tranh tran CPU va don tiep tuc hang doi

  delay 20

