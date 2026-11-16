/*
  Лабораторная работа №3. Вариант 4.
  Экспертная система с прямой цепочкой рассуждений
  для определения причины неработоспособности компьютера.
  Среда разработки: Visual Prolog 5.2.
*/

domains
    slist = symbol*                     % список имен условий правила

global database
    known(symbol, symbol, integer)       % known(Ответ, Факт, Глубина)
    fired(symbol)                       % признак срабатывания правила на проходе
    pass_no(integer)                    % номер текущего прохода прямого вывода

predicates
    nondeterm run                       % главный предикат программы
    clear_db                            % очистка рабочей памяти
    clear_fired                         % сброс флага срабатывания
    clear_pass                          % сброс номера прохода
    nondeterm ask_all                   % опрос пользователя
    nondeterm ask(symbol)               % задать один вопрос
    nondeterm yes_char(char)            % проверка ответа "да"
    nondeterm forward                   % прямой вывод до неподвижной точки
    nondeterm all_known(slist, slist, integer, integer)
                                        % проверка условий и вычисление глубины
    nondeterm max2(integer, integer, integer)
                                        % максимум двух чисел
    any_cause                           % есть ли хотя бы одна выведенная причина
    nondeterm show_results              % вывод результата
    nondeterm show_all_causes           % вывод всех найденных причин
    nondeterm question_text(symbol, string)
                                        % текст вопроса для признака
    nondeterm fact_name(symbol, string) % текстовая расшифровка факта
    nondeterm rule(symbol, slist, slist)
                                        % правило: заключение, положительные
                                        % и отрицательные условия
    nondeterm cause(symbol)             % список возможных причин

clauses
    % ------------------------------------------------------------
    % Главный предикат: очистка памяти, опрос, прямой вывод, итог
    % ------------------------------------------------------------
    run :-
        clear_db,
        clear_fired,
        clear_pass,
        assertz(pass_no(1)),
        write("Экспертная система: причины неработоспособности компьютера"), nl,
        write("Вариант 4: прямая цепочка рассуждений"), nl,
        write("Отвечайте y (да) или n (нет)."), nl, nl,
        ask_all,
        nl,
        write("--- Прямой вывод ---"), nl,
        forward,
        nl,
        show_results.

    clear_db :-
        retractall(known(_, _, _)).

    clear_fired :-
        retractall(fired(_)).

    clear_pass :-
        retractall(pass_no(_)).

    % ------------------------------------------------------------
    % Опрос пользователя: все шесть признаков запрашиваются один раз
    % ------------------------------------------------------------
    ask_all :-
        ask(power),
        ask(fan),
        ask(display),
        ask(beep),
        ask(os),
        ask(overheat).

    ask(S) :-
        question_text(S, Q),
        write(Q, " (y/n): "),
        readln(Reply),
        frontchar(Reply, C, _),
        yes_char(C), !,
        assertz(known(yes, S, 0)).
    ask(S) :-
        assertz(known(no, S, 0)).

    yes_char('y').
    yes_char('Y').

    % ------------------------------------------------------------
    % Прямой вывод: на каждом проходе просматриваются все правила.
    % Если все условия правила уже известны, заключение добавляется
    % в рабочую память. Проходы повторяются, пока появляются новые
    % факты. Глубина заключения = максимум глубин условий + 1.
    % ------------------------------------------------------------
    forward :-
        clear_fired,
        pass_no(N),
        write("--- Проход ", N, " ---"), nl,
        rule(C, Pos, Neg),
        not(known(yes, C, _)),
        all_known(Pos, Neg, 0, D0),
        D = D0 + 1,
        D <= 4,
        fact_name(C, Name),
        assertz(known(yes, C, D)),
        assertz(fired(yes)),
        write("  Сработало правило: ", Name, " (глубина ", D, ")"), nl,
        fail.
    forward :-
        fired(_),
        !,
        pass_no(N),
        N1 = N + 1,
        retract(pass_no(N)),
        assertz(pass_no(N1)),
        forward.
    forward.

    % Проверка положительных и отрицательных условий правила.
    all_known([], [], D, D) :- !.
    all_known([P|Ps], Neg, D0, D) :-
        known(yes, P, DP),
        max2(D0, DP, D1),
        all_known(Ps, Neg, D1, D).
    all_known([], [N|Ns], D0, D) :-
        known(no, N, _),
        all_known([], Ns, D0, D).

    max2(A, B, A) :- A >= B, !.
    max2(_, B, B).

    % ------------------------------------------------------------
    % Вывод результата
    % ------------------------------------------------------------
    any_cause :-
        cause(C),
        known(yes, C, _),
        !.

    show_results :-
        any_cause,
        !,
        write("Найденные причины:"), nl,
        show_all_causes.
    show_results :-
        write("Причина не определена."), nl.

    show_all_causes :-
        cause(C),
        known(yes, C, D),
        fact_name(C, Name),
        write(" - ", Name, " (глубина ", D, ")"), nl,
        fail.
    show_all_causes.

    % ------------------------------------------------------------
    % Тексты вопросов
    % ------------------------------------------------------------
    question_text(power, "Компьютер включается (есть реакция на кнопку питания)?").
    question_text(fan, "Вращается вентилятор блока питания или процессора?").
    question_text(display, "Есть изображение на мониторе?").
    question_text(beep, "Слышны звуковые сигналы BIOS?").
    question_text(os, "Начинается загрузка операционной системы?").
    question_text(overheat, "Компьютер перегревается или выключается через некоторое время?").

    % ------------------------------------------------------------
    % База правил.
    % Правила сгруппированы в обратном порядке: сначала причины,
    % затем гипотезы третьего, второго и первого уровней. Такой
    % порядок не влияет на результат, но делает трассировку
    % наглядной: факты накапливаются по уровням за несколько проходов.
    % ------------------------------------------------------------

    % Причины (12)
    rule(bad_outlet, [no_power_no_fan, post_ok], []).
    rule(bad_psu, [no_power_no_fan, post_error], []).
    rule(bad_power_button, [no_power, fan_ok], []).
    rule(bad_motherboard, [power_no_fan, no_video, post_ok], []).
    rule(bad_cpu, [power_no_fan, post_error], []).
    rule(bad_ram, [power_fan, no_video_post_error], []).
    rule(bad_gpu, [power_fan, no_video_post_ok_no_os], []).
    rule(bad_monitor, [power_fan, no_video_post_ok_os], []).
    rule(bad_hdd, [power_fan, video_ok_post_ok_no_os, cool], []).
    rule(bad_os, [power_fan, video_ok_post_ok_no_os, hot], []).
    rule(bad_bios, [power_fan, video_ok_post_error], []).
    rule(bad_cooler, [power_fan, video_ok_post_ok_os_hot], []).

    % Промежуточные гипотезы третьего уровня (4)
    rule(no_video_post_ok_os, [no_video_post_ok, boot_ok], []).
    rule(no_video_post_ok_no_os, [no_video_post_ok, boot_error], []).
    rule(video_ok_post_ok_no_os, [video_ok_post_ok, boot_error], []).
    rule(video_ok_post_ok_os_hot, [video_ok_post_ok, boot_ok, hot], []).

    % Промежуточные гипотезы второго уровня (11)
    rule(power_fan, [power_ok, fan_ok], []).
    rule(power_no_fan, [power_ok, fan_fail], []).
    rule(no_power_no_fan, [no_power, fan_fail], []).
    rule(no_video_post_ok, [no_video, post_ok], []).
    rule(no_video_post_error, [no_video, post_error], []).
    rule(video_ok_post_ok, [video_ok, post_ok], []).
    rule(video_ok_post_error, [video_ok, post_error], []).
    rule(boot_cool, [boot_ok, cool], []).
    rule(boot_hot, [boot_ok, hot], []).
    rule(boot_error_cool, [boot_error, cool], []).
    rule(boot_error_hot, [boot_error, hot], []).

    % Промежуточные гипотезы первого уровня (12)
    rule(no_power, [], [power]).
    rule(power_ok, [power], []).
    rule(fan_ok, [fan], []).
    rule(fan_fail, [], [fan]).
    rule(no_video, [], [display]).
    rule(video_ok, [display], []).
    rule(post_ok, [], [beep]).
    rule(post_error, [beep], []).
    rule(boot_ok, [os], []).
    rule(boot_error, [], [os]).
    rule(hot, [overheat], []).
    rule(cool, [], [overheat]).

    % ------------------------------------------------------------
    % Список причин
    % ------------------------------------------------------------
    cause(bad_outlet).
    cause(bad_psu).
    cause(bad_power_button).
    cause(bad_motherboard).
    cause(bad_cpu).
    cause(bad_ram).
    cause(bad_gpu).
    cause(bad_monitor).
    cause(bad_hdd).
    cause(bad_os).
    cause(bad_bios).
    cause(bad_cooler).

    % ------------------------------------------------------------
    % Текстовые расшифровки фактов
    % ------------------------------------------------------------
    fact_name(no_power, "нет питания").
    fact_name(power_ok, "питание есть").
    fact_name(fan_ok, "вентилятор вращается").
    fact_name(fan_fail, "вентилятор не вращается").
    fact_name(no_video, "нет изображения").
    fact_name(video_ok, "изображение есть").
    fact_name(post_ok, "POST без ошибок").
    fact_name(post_error, "ошибка POST (звуковой сигнал)").
    fact_name(boot_ok, "операционная система загружается").
    fact_name(boot_error, "операционная система не загружается").
    fact_name(hot, "есть перегрев").
    fact_name(cool, "перегрева нет").

    fact_name(power_fan, "питание и вентилятор в норме").
    fact_name(power_no_fan, "питание есть, вентилятор не вращается").
    fact_name(no_power_no_fan, "нет питания и не вращается вентилятор").
    fact_name(no_video_post_ok, "нет изображения, POST без ошибок").
    fact_name(no_video_post_error, "нет изображения, ошибка POST").
    fact_name(video_ok_post_ok, "изображение есть, POST без ошибок").
    fact_name(video_ok_post_error, "изображение есть, ошибка POST").
    fact_name(boot_cool, "ОС загружается, перегрева нет").
    fact_name(boot_hot, "ОС загружается, есть перегрев").
    fact_name(boot_error_cool, "ОС не загружается, перегрева нет").
    fact_name(boot_error_hot, "ОС не загружается, есть перегрев").

    fact_name(no_video_post_ok_os, "нет изображения, POST без ошибок, ОС загружается").
    fact_name(no_video_post_ok_no_os, "нет изображения, POST без ошибок, ОС не загружается").
    fact_name(video_ok_post_ok_no_os, "изображение и POST в норме, ОС не загружается").
    fact_name(video_ok_post_ok_os_hot, "изображение и POST в норме, ОС загружается, есть перегрев").

    fact_name(bad_outlet, "Нет напряжения в сети (неисправна розетка или кабель питания)").
    fact_name(bad_psu, "Неисправен блок питания").
    fact_name(bad_power_button, "Неисправна кнопка питания").
    fact_name(bad_motherboard, "Неисправна материнская плата").
    fact_name(bad_cpu, "Неисправен процессор").
    fact_name(bad_ram, "Неисправна оперативная память").
    fact_name(bad_gpu, "Неисправна видеокарта").
    fact_name(bad_monitor, "Неисправен монитор или кабель").
    fact_name(bad_hdd, "Неисправен жёсткий диск").
    fact_name(bad_os, "Повреждена операционная система").
    fact_name(bad_bios, "Неисправен BIOS").
    fact_name(bad_cooler, "Неисправна система охлаждения (кулер)").

goal
    run.
