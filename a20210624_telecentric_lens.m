%% focal point ylf) outside of tank


syms Lw dx1 fFL dx2 fRL dx3
    ;
T0=[1 Lw;0 1];
T1=[1 dx1;0 1];
R0=[1 0; -1/fFL 1];
T2=[1 fFL;0 1];
T3=[1 dx2;0 1];
R1=[1 0; -1/fRL 1];
T4=[1 dx3; 0 1];

% entire optical path
A=T4*R1*T3*T2*R0*T1*T0
% just telecentric
% A=R1*T3*T2*R0
theta0=0%1/4/360.*2*pi
x0=1;
X=[x0;theta0];
%%
Xn=A
f( Lw , dx1, fFL, fRL , dx2) =Xn
%%
% Lw=81.5e-3;
% fFL=70.1e-3;
% dx1=36.4e-3;
% ybp=0.5e-3;
% fRL = -17.2e-3;
% dx2 = 9.4e-3;
f( 81.5e-3,36.4e-3,70.1e-3,-17.2e-3,9.4e-3)
%%
theta=asin(1.1e-2/2/500e-3);

%%

